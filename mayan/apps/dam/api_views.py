from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.rest_api import generics as mayan_generics
from mayan.apps.templating.classes import AJAXTemplate

from .models import DocumentAIAnalysis, DAMMetadataPreset
from .serializers import DocumentAIAnalysisSerializer, DAMMetadataPresetSerializer
from .tasks import analyze_document_with_ai


class DocumentAIAnalysisViewSet(ModelViewSet):
    """
    API endpoint for managing AI analysis of documents.
    """
    serializer_class = DocumentAIAnalysisSerializer
    queryset = DocumentAIAnalysis.objects.all()

    @action(detail=False, methods=['post'])
    def analyze(self, request):
        """
        Start AI analysis for a specific document.
        """
        document_id = request.data.get('document_id')

        if not document_id:
            return Response(
                {'error': 'document_id field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from mayan.apps.documents.models import Document
            from mayan.apps.acls.models import AccessControlList
            from mayan.apps.documents.permissions import permission_document_view

            document = Document.objects.get(pk=document_id)

            # Check permissions
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=request.user
            )

            # Get or create analysis
            ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
                document=document,
                defaults={'analysis_status': 'pending'}
            )

            # Start analysis
            analyze_document_with_ai.delay(document.id)

            return Response({
                'message': f'AI analysis started for document {document_id}',
                'analysis_id': ai_analysis.id,
                'status': 'started'
            })

        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def reanalyze(self, request, pk=None):
        """
        Trigger re-analysis of a document with AI.
        """
        ai_analysis = self.get_object()

        # Reset status and trigger analysis
        ai_analysis.analysis_status = 'pending'
        ai_analysis.save()

        analyze_document_with_ai.delay(ai_analysis.document.id)

        return Response({
            'message': 'AI re-analysis scheduled',
            'status': 'pending'
        })

    @action(detail=False, methods=['post'])
    def bulk_analyze(self, request):
        """
        Trigger AI analysis for multiple documents.
        """
        document_ids = request.data.get('document_ids', [])

        if not document_ids:
            return Response(
                {'error': 'document_ids field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Schedule bulk analysis
        from .tasks import bulk_analyze_documents
        bulk_analyze_documents.delay(document_ids)

        return Response({
            'message': f'AI analysis scheduled for {len(document_ids)} documents',
            'document_ids': document_ids
        })


class DAMMetadataPresetViewSet(ModelViewSet):
    """
    API endpoint for managing DAM metadata presets.
    """
    serializer_class = DAMMetadataPresetSerializer
    queryset = DAMMetadataPreset.objects.all()

    @action(detail=True, methods=['post'])
    def test_preset(self, request, pk=None):
        """
        Test a metadata preset with a sample document.
        """
        preset = self.get_object()
        document_id = request.data.get('document_id')

        if not document_id:
            return Response(
                {'error': 'document_id field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # TODO: Implement preset testing logic
        return Response({
            'message': f'Preset {preset.name} testing not yet implemented',
            'preset': preset.name,
            'document_id': document_id
        })


class AIAnalysisStatusView(mayan_generics.GenericAPIView):
    """
    API endpoint to get AI analysis status for a document.
    """

    @action(detail=False, methods=['get'])
    def get_status(self, request):
        """
        Get AI analysis status for a document.
        """
        document_id = request.query_params.get('document_id')

        if not document_id:
            return Response(
                {'error': 'document_id query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ai_analysis = DocumentAIAnalysis.objects.get(document_id=document_id)
            return Response({
                'document_id': document_id,
                'status': ai_analysis.analysis_status,
                'provider': ai_analysis.ai_provider,
                'completed_at': ai_analysis.analysis_completed,
                'has_description': bool(ai_analysis.ai_description),
                'tags_count': len(ai_analysis.get_ai_tags_list()),
                'colors_count': len(ai_analysis.get_dominant_colors_list()),
                'has_alt_text': bool(ai_analysis.alt_text)
            })
        except DocumentAIAnalysis.DoesNotExist:
            return Response({
                'document_id': document_id,
                'status': 'not_analyzed',
                'message': 'Document has not been analyzed with AI yet'
            })


class DAMDocumentDetailView(generics.RetrieveAPIView):
    """
    Render DAM AJAX template for a specific document.
    """
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        document_id = self.request.query_params.get('document_id')
        if not document_id:
            return None

        try:
            document = Document.objects.get(pk=document_id)
            # Check permissions
            from mayan.apps.acls.models import AccessControlList
            AccessControlList.objects.check_access(
                obj=document,
                permissions=(permission_document_view,),
                user=self.request.user
            )
            return document
        except (Document.DoesNotExist, Exception):
            return None

    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()
        if not document:
            return Response({'error': 'Document not found or access denied'}, status=404)

        # Get or create AI analysis
        ai_analysis, created = DocumentAIAnalysis.objects.get_or_create(
            document=document,
            defaults={'analysis_status': 'pending'}
        )

        # Render AJAX template with context
        template = AJAXTemplate.get('dam_document_detail')
        context = {
            'document': document,
            'ai_analysis': ai_analysis,
            'request': request
        }

        # Manually render template with custom context
        from django.template import Context, Engine
        from django.template.loader import get_template

        django_template = get_template(template.template_name)
        rendered_content = django_template.render(context, request)

        # Calculate hash
        import hashlib
        content_bytes = rendered_content.encode('utf-8')
        hex_hash = hashlib.sha256(content_bytes).hexdigest()

        return Response({
            'name': template.name,
            'html': rendered_content,
            'hex_hash': hex_hash
        })
