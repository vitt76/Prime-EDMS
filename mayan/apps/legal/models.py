from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserConsentLog(models.Model):
    """
    Audit log of user cookie/consent choices for compliance (152-FZ, GDPR-style).
    No tenant/organization — global legal audit.
    """
    CONSENT_FULL = 'full'
    CONSENT_NECESSARY = 'necessary'
    CONSENT_REJECTED = 'rejected'

    CONSENT_TYPE_CHOICES = (
        (CONSENT_FULL, _('Accept all')),
        (CONSENT_NECESSARY, _('Necessary only')),
        (CONSENT_REJECTED, _('Rejected')),
    )

    ip_address = models.GenericIPAddressField(
        blank=True, null=True,
        verbose_name=_('IP address'),
        help_text=_('Filled from request on server')
    )
    user_agent = models.TextField(
        blank=True, default='',
        verbose_name=_('User-Agent'),
        help_text=_('Filled from request on server')
    )
    consent_type = models.CharField(
        max_length=20,
        choices=CONSENT_TYPE_CHOICES,
        db_index=True,
        verbose_name=_('Consent type')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_('Timestamp')
    )
    session_id = models.CharField(
        max_length=255,
        blank=True, default='',
        verbose_name=_('Session ID'),
        help_text=_('Cookie/session value from client for correlation')
    )
    url_referer = models.URLField(
        max_length=2048,
        blank=True, default='',
        verbose_name=_('URL referer')
    )

    class Meta:
        app_label = 'legal'
        verbose_name = _('User consent log entry')
        verbose_name_plural = _('User consent log')
        ordering = ('-timestamp',)
