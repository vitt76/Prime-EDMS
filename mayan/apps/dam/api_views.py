from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from mayan.apps.rest_api import generics as mayan_generics

from .models import DocumentAIAnalysis, DAMMetadataPreset
from .serializers import DocumentAIAnalysisSerializer, DAMMetadataPresetSerializer
from .tasks import analyze_document_with_ai


class DocumentAIAnalysisViewSet(ModelViewSet):
    """
    API endpoint for managing AI analysis of documents.
    """
    serializer_class = DocumentAIAnalysisSerializer
    queryset = DocumentAIAnalysis.objects.all()

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
