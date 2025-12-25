import json
import logging

from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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
        Get the share link.
        """
        return super().get_object(queryset)

    def get(self, request, *args, **kwargs):
        """
        Handle GET request and check if link is valid.
        """
        try:
            share_link = self.get_object()
        except Http404:
            raise

        # Check if link is valid
        if not share_link.is_valid():
            # Determine reason for expiration
            from django.utils import timezone
            reason = None
            if share_link.expires_at and timezone.now() > share_link.expires_at:
                reason = _("Срок действия ссылки истёк.")
            elif share_link.max_downloads and share_link.downloads_count >= share_link.max_downloads:
                reason = _("Достигнут лимит скачиваний.")
            elif share_link.max_views and share_link.views_count >= share_link.max_views:
                reason = _("Достигнут лимит просмотров.")
            
            # Return JSON response for API requests
            if request.headers.get('Accept', '').startswith('application/json'):
                return JsonResponse(
                    {'error': 'Link expired', 'reason': str(reason) if reason else 'Unknown'},
                    status=410
                )
            # For browser requests, show expired page
            return render(
                request,
                'distribution/portal/link_expired.html',
                {
                    'token': share_link.token,
                    'reason': reason
                },
                status=410
            )

        # Check password if set
        if share_link.password_hash:
            password = request.GET.get('password') or request.POST.get('password')
            if not password or not share_link.check_password(password):
                # Store token in session for password form
                request.session[f'share_link_{share_link.token}'] = True
                raise Http404(_("Password required for this link."))

        # Continue with normal DetailView processing
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        share_link = self.object

        # Record access
        share_link.record_access(self.request)

        # For single rendition share link, just show that rendition
        rendition = share_link.rendition
        publication_items = [{
            'item': rendition.publication_item,
            'renditions': [rendition],
            'original_file': rendition.publication_item.document_file
        }]

        context.update({
            'publication_items': publication_items,
            'can_download': share_link.can_download(),
        })

        return context


@public
def share_link_view(request, token):
    """
    Public view for direct access to a rendition file via share link token.
    Displays the file inline in the browser instead of downloading.
    """
    # Get share link
    share_link = get_object_or_404(ShareLink, token=token)

    # Check if link is valid
    if not share_link.is_valid():
        # Determine reason for expiration
        from django.utils import timezone
        reason = None
        if share_link.expires_at and timezone.now() > share_link.expires_at:
            reason = _("Срок действия ссылки истёк.")
        elif share_link.max_downloads and share_link.downloads_count >= share_link.max_downloads:
            reason = _("Достигнут лимит скачиваний.")
        elif share_link.max_views and share_link.views_count >= share_link.max_views:
            reason = _("Достигнут лимит просмотров.")
        
        # Return JSON response for API requests
        if request.headers.get('Accept', '').startswith('application/json'):
            return JsonResponse(
                {'error': 'Link expired', 'reason': str(reason) if reason else 'Unknown'},
                status=410
            )
        # For browser requests, show expired page
        return render(
            request,
            'distribution/portal/link_expired.html',
            {
                'token': token,
                'reason': reason
            },
            status=410
        )

    # Check password if set
    if share_link.password_hash:
        password = request.GET.get('password') or request.POST.get('password')
        if not password or not share_link.check_password(password):
            # Return JSON response for API requests
            if request.headers.get('Accept', '').startswith('application/json'):
                return JsonResponse(
                    {'error': 'Password required', 'password_required': True},
                    status=403
                )
            # For browser requests, show password form
            # Show error if password was provided but incorrect
            error = 'invalid' if password else None
            return render(
                request,
                'distribution/portal/password_required.html',
                {
                    'token': token,
                    'error': error
                },
                status=403
            )

    # Check if download is allowed (using can_download for consistency, though it's inline view)
    if not share_link.can_download():
        raise Http404(_("Access limit reached for this link."))

    # Get rendition (now directly from share_link.rendition)
    rendition = share_link.rendition

    # Check if rendition is completed
    if rendition.status != 'completed':
        raise Http404(_("Rendition is not ready yet."))

    # Determine content type
    content_type = 'application/octet-stream'
    if rendition.preset.format == 'jpeg':
        content_type = 'image/jpeg'
    elif rendition.preset.format == 'png':
        content_type = 'image/png'
    elif rendition.preset.format == 'pdf':
        content_type = 'application/pdf'
    elif rendition.preset.format == 'mp4':
        content_type = 'video/mp4'

    filename = rendition.file.name.split('/')[-1]

    # If max_downloads is set, we need to force download (attachment) to properly track downloads
    # Otherwise, show inline for better UX
    has_download_limit = share_link.max_downloads is not None
    
    if has_download_limit:
        # If download limit is set, force download to track it properly
        # Record download (this increments downloads_count)
        share_link.record_download(request, rendition)
        
        response = HttpResponse(rendition.file, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        # No download limit, show inline for better viewing experience
        # Record access (this increments views_count only)
        share_link.record_access(request)
        
        response = HttpResponse(rendition.file, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        # Add cache headers for better performance
        response['Cache-Control'] = 'private, max-age=3600'

    try:
        return response
    except Exception as e:
        logger.error(f"Error serving share link {token}: {e}")
        raise Http404(_("Error accessing file."))


@public
@csrf_exempt
@require_http_methods(["POST"])
def check_share_link_password(request, token):
    """
    API endpoint to check password for share link.
    """
    share_link = get_object_or_404(ShareLink, token=token)
    
    try:
        data = json.loads(request.body)
        password = data.get('password', '')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse(
            {'error': 'Invalid request data'},
            status=400
        )
    
    if share_link.check_password(password):
        return JsonResponse({'valid': True})
    else:
        return JsonResponse(
            {'valid': False, 'error': 'Invalid password'},
            status=403
        )


@public
def download_rendition(request, token, rendition_id):
    """
    Public view for downloading a specific rendition.
    """
    # Get share link
    share_link = get_object_or_404(ShareLink, token=token)

    # Check if link is valid
    if not share_link.is_valid():
        messages.error(request, _("This link has expired or reached its limit."))
        return redirect('distribution:portal', token=token)

    # Check password if set
    if share_link.password_hash:
        password = request.GET.get('password') or request.POST.get('password')
        if not password or not share_link.check_password(password):
            messages.error(request, _("Password required for this link."))
            return redirect('distribution:portal', token=token)

    # Check if download is allowed
    if not share_link.can_download():
        messages.error(request, _("Download limit reached for this link."))
        return redirect('distribution:portal', token=token)

    # Get rendition
    rendition = get_object_or_404(
        GeneratedRendition,
        id=rendition_id,
        publication_item=share_link.rendition.publication_item,
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
