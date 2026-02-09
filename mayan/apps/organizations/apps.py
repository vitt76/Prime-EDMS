import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig

from .patches import patch_HttpRequest, patch_document_managers

logger = logging.getLogger(name=__name__)


class OrganizationsApp(MayanAppConfig):
    app_namespace = 'organizations'
    app_url = 'organizations'
    name = 'mayan.apps.organizations'
    verbose_name = _('Organizations')

    def ready(self):
        super().ready()

        patch_HttpRequest()
        patch_document_managers()

        # Connect quota enforcement signal
        self._connect_quota_signals()

        # Connect cache invalidation signals
        self._connect_cache_invalidation_signals()

    def _connect_quota_signals(self):
        """Connect pre_save signal for storage quota enforcement."""
        try:
            from django.db.models.signals import pre_save
            from mayan.apps.documents.models import DocumentFile
            from .quota import on_document_file_pre_save

            pre_save.connect(
                on_document_file_pre_save,
                sender=DocumentFile,
                dispatch_uid='organizations_storage_quota_check'
            )
            logger.debug('Connected storage quota signal to DocumentFile')
        except Exception as exc:
            logger.warning(
                'Could not connect storage quota signal: %s', exc
            )

    def _connect_cache_invalidation_signals(self):
        """
        Connect post_save / post_delete signals for cache invalidation.

        Invalidates Redis-cached quota values when relevant models change:
        - DocumentFile -> storage cache
        - UserOrganizationRole -> user count cache
        - DocumentAIAnalysis -> AI analyses cache
        """
        from django.db.models.signals import post_delete, post_save

        # --- Storage cache invalidation ---
        try:
            from mayan.apps.documents.models import DocumentFile

            def _invalidate_storage_cache(sender, instance, **kwargs):
                try:
                    org = getattr(instance.document, 'organization', None)
                    if org is not None:
                        org.invalidate_storage_cache()
                except Exception as exc:
                    logger.debug(
                        'Storage cache invalidation failed for %s: %s',
                        sender.__name__, exc
                    )

            post_save.connect(
                _invalidate_storage_cache,
                sender=DocumentFile,
                dispatch_uid='org_cache_inv_docfile_save'
            )
            post_delete.connect(
                _invalidate_storage_cache,
                sender=DocumentFile,
                dispatch_uid='org_cache_inv_docfile_del'
            )
        except Exception as exc:
            logger.warning(
                'Could not connect storage cache invalidation: %s', exc
            )

        # --- User count cache invalidation ---
        try:
            from .models import UserOrganizationRole

            def _invalidate_users_cache(sender, instance, **kwargs):
                try:
                    instance.organization.invalidate_users_cache()
                except Exception as exc:
                    logger.debug(
                        'Users cache invalidation failed for %s: %s',
                        sender.__name__, exc
                    )

            post_save.connect(
                _invalidate_users_cache,
                sender=UserOrganizationRole,
                dispatch_uid='org_cache_inv_uor_save'
            )
            post_delete.connect(
                _invalidate_users_cache,
                sender=UserOrganizationRole,
                dispatch_uid='org_cache_inv_uor_del'
            )
        except Exception as exc:
            logger.warning(
                'Could not connect users cache invalidation: %s', exc
            )

        # --- AI analyses cache invalidation ---
        try:
            from mayan.apps.dam.models import DocumentAIAnalysis

            def _invalidate_ai_cache(sender, instance, **kwargs):
                try:
                    org = getattr(instance.document, 'organization', None)
                    if org is not None:
                        org.invalidate_ai_cache()
                except Exception as exc:
                    logger.debug(
                        'AI cache invalidation failed for %s: %s',
                        sender.__name__, exc
                    )

            post_save.connect(
                _invalidate_ai_cache,
                sender=DocumentAIAnalysis,
                dispatch_uid='org_cache_inv_ai_save'
            )
            post_delete.connect(
                _invalidate_ai_cache,
                sender=DocumentAIAnalysis,
                dispatch_uid='org_cache_inv_ai_del'
            )
        except Exception as exc:
            logger.warning(
                'Could not connect AI cache invalidation: %s', exc
            )
