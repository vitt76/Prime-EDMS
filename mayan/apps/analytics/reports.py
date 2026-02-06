"""Analytics report generation utilities (PDF/exports)."""

from __future__ import annotations

import io
from datetime import timedelta
from typing import Optional

from django.db.models import Count
from django.utils import timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from mayan.apps.documents.models import Document

from .models import AssetEvent, Campaign, CampaignAsset


class CampaignPDFReport:
    """Generate a basic campaign PDF report (production-safe, no external deps)."""

    def __init__(self, *, campaign_id: str, days: int = 30):
        self.campaign_id = campaign_id
        self.days = int(days)

    def render(self) -> bytes:
        campaign = Campaign.objects.filter(pk=self.campaign_id).first()
        if not campaign:
            raise ValueError('Campaign not found')

        date_from = timezone.now() - timedelta(days=self.days)
        document_ids = list(CampaignAsset.objects.filter(campaign=campaign).values_list('document_id', flat=True))

        events_qs = AssetEvent.objects.filter(document_id__in=document_ids, timestamp__gte=date_from)
        views = events_qs.filter(event_type=AssetEvent.EVENT_TYPE_VIEW).count()
        downloads = events_qs.filter(event_type=AssetEvent.EVENT_TYPE_DOWNLOAD).count()
        shares = events_qs.filter(event_type=AssetEvent.EVENT_TYPE_SHARE).count()

        roi = None
        try:
            roi = campaign.get_roi()
        except Exception:
            roi = None

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        width, height = A4

        x = 18 * mm
        y = height - 20 * mm
        c.setFont('Helvetica-Bold', 14)
        c.drawString(x, y, f'Отчет по кампании: {campaign.label}')

        y -= 8 * mm
        c.setFont('Helvetica', 10)
        c.drawString(x, y, f'Период: последние {self.days} дней')

        y -= 10 * mm
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x, y, 'Сводка')

        y -= 7 * mm
        c.setFont('Helvetica', 10)
        c.drawString(x, y, f'Просмотры: {views}')
        y -= 5 * mm
        c.drawString(x, y, f'Скачивания: {downloads}')
        y -= 5 * mm
        c.drawString(x, y, f'Шеринг: {shares}')
        y -= 5 * mm
        c.drawString(x, y, f'ROI: {roi if roi is not None else "—"}')

        y -= 12 * mm
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x, y, 'Топ-10 ассетов по скачиваниям')

        y -= 7 * mm
        c.setFont('Helvetica', 9)
        top_rows = list(
            AssetEvent.objects.filter(
                document_id__in=document_ids,
                event_type=AssetEvent.EVENT_TYPE_DOWNLOAD,
                timestamp__gte=date_from
            )
            .values('document_id')
            .annotate(downloads_count=Count('id'))
            .order_by('-downloads_count')[:10]
        )
        label_map = dict(
            Document.valid.filter(pk__in=[r['document_id'] for r in top_rows]).values_list('pk', 'label')
        )

        if not top_rows:
            c.drawString(x, y, 'Нет данных за выбранный период.')
        else:
            for idx, row in enumerate(top_rows, start=1):
                label = label_map.get(row['document_id'], '')
                c.drawString(x, y, f'{idx}. {label} — {int(row["downloads_count"])}')
                y -= 5 * mm
                if y < 20 * mm:
                    c.showPage()
                    y = height - 20 * mm
                    c.setFont('Helvetica', 9)

        c.showPage()
        c.save()
        return buf.getvalue()


