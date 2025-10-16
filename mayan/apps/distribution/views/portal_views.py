import logging

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from stronghold.decorators import public

from ..models import ShareLink, GeneratedRendition

logger = logging.getLogger(name=__name__)


class PublicationPortalView(DetailView):
    """
    Public view for accessing a publication via share link.
    """
    model = ShareLink
    slug_field = 'token'
    slug_url_kwarg = 'token'
    template_name = 'distribution/portal/publication_detail.html'
    context_object_name = 'share_link'

    @public
    def dispatch(self, request, *args, **kwargs):
        """
        Allow public access to this view.
        """
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        """
        Get the share link and validate it.
        """
        share_link = super().get_object(queryset)

        # Check if link is valid
        if not share_link.is_valid():
            raise Http404(_("This link has expired or reached its download limit."))

        return share_link

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        share_link = self.object

        # Record access
        share_link.record_access(self.request)

        # Get all publication items with their renditions
        publication_items = []
        for item in share_link.publication.items.all():
            renditions = GeneratedRendition.objects.filter(
                publication_item=item,
                status='completed'
            ).select_related('preset')

            publication_items.append({
                'item': item,
                'renditions': renditions,
                'original_file': item.document_file
            })

        context.update({
            'publication_items': publication_items,
            'can_download': share_link.can_download(),
        })

        return context


@public
def download_rendition(request, token, rendition_id):
    """
    Public view for downloading a specific rendition.
    """
    # Get share link
    share_link = get_object_or_404(ShareLink, token=token)

    # Check if link is valid
    if not share_link.is_valid():
        messages.error(request, _("This link has expired or reached its download limit."))
        return redirect('distribution:portal', token=token)

    # Check if download is allowed
    if not share_link.can_download():
        messages.error(request, _("Download limit reached for this link."))
        return redirect('distribution:portal', token=token)

    # Get rendition
    rendition = get_object_or_404(
        GeneratedRendition,
        id=rendition_id,
        publication_item__publication=share_link.publication,
        status='completed'
    )

    # Record download
    share_link.record_download(request, rendition)

    # Serve file
    try:
        response = HttpResponse(rendition.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{rendition.file.name.split("/")[-1]}"'

        # Set content type based on format
        if rendition.preset.format == 'jpeg':
            response['Content-Type'] = 'image/jpeg'
        elif rendition.preset.format == 'png':
            response['Content-Type'] = 'image/png'
        elif rendition.preset.format == 'pdf':
            response['Content-Type'] = 'application/pdf'
        elif rendition.preset.format == 'mp4':
            response['Content-Type'] = 'video/mp4'

        return response

    except Exception as e:
        logger.error(f"Error serving rendition {rendition_id}: {e}")
        messages.error(request, _("Error downloading file."))
        return redirect('distribution:portal', token=token)
