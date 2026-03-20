import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig

from .patches import (
    get_runtime_patch_status, patch_HttpRequest, patch_document_managers,
    patch_organization_fields
)

logger = logging.getLogger(name=__name__)


class OrganizationsApp(MayanAppConfig):
    app_namespace = 'organizations'
    app_url = 'organizations'
    name = 'mayan.apps.organizations'
    verbose_name = _('Organizations')

    def ready(self):
        super().ready()

        patch_HttpRequest()
        patch_organization_fields()
        patch_document_managers()
        logger.info(
            'Organization runtime patch status: %s',
            get_runtime_patch_status()
        )

        # Ensure Document.organization is always set before DB insert.
        self._connect_document_tenant_binding_signal()
        self._connect_ai_analysis_tenant_binding_signal()
        self._connect_assetevent_tenant_binding_signal()
        self._connect_sharelink_tenant_binding_signal()
        self._connect_cabinet_tenant_binding_signal()

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

    def _connect_document_tenant_binding_signal(self):
        """
        Connect pre_save signal to auto-bind organization for Document.

        Document.organization is NOT NULL at DB level. Some create paths
        (including /api/v4/documents/) do not pass organization explicitly,
        so we must inject it from tenant context before insert.
        """
        try:
            from django.db.models.signals import pre_save
            from mayan.apps.documents.models import Document

            from .literals import DEFAULT_ORGANIZATION_SLUG
            from .managers import get_current_organization
            from .models import Organization

            def _bind_document_organization(sender, instance, **kwargs):
                # Respect explicit assignment done by caller.
                if getattr(instance, 'organization_id', None):
                    return

                organization = get_current_organization()

                # Defensive fallback for non-request flows.
                if organization is None:
                    organization = Organization.objects.filter(
                        slug=DEFAULT_ORGANIZATION_SLUG
                    ).first()

                if organization is not None:
                    instance.organization = organization

            pre_save.connect(
                _bind_document_organization,
                sender=Document,
                dispatch_uid='organizations_bind_document_organization',
                weak=False
            )
            logger.debug('Connected document tenant binding signal')
        except Exception as exc:
            logger.warning(
                'Could not connect document tenant binding signal: %s', exc
            )

    def _connect_ai_analysis_tenant_binding_signal(self):
        """
        Connect pre_save signal to auto-bind organization for DocumentAIAnalysis.

        Priority:
        1) Existing explicit assignment.
        2) Current tenant context.
        3) Parent document organization.
        4) Default organization fallback.
        """
        try:
            from django.db.models.signals import pre_save

            from mayan.apps.dam.models import DocumentAIAnalysis

            from .literals import DEFAULT_ORGANIZATION_SLUG
            from .managers import get_current_organization
            from .models import Organization

            def _bind_ai_analysis_organization(sender, instance, **kwargs):
                if getattr(instance, 'organization_id', None):
                    return

                organization = get_current_organization()

                if organization is None:
                    document = getattr(instance, 'document', None)
                    organization = getattr(document, 'organization', None)

                if organization is None:
                    organization = Organization.objects.filter(
                        slug=DEFAULT_ORGANIZATION_SLUG
                    ).first()

                if organization is not None:
                    instance.organization = organization

            pre_save.connect(
                _bind_ai_analysis_organization,
                sender=DocumentAIAnalysis,
                dispatch_uid='organizations_bind_ai_analysis_organization',
                weak=False
            )
            logger.debug('Connected AI analysis tenant binding signal')
        except Exception as exc:
            logger.warning(
                'Could not connect AI analysis tenant binding signal: %s', exc
            )

    def _connect_assetevent_tenant_binding_signal(self):
        """
        Connect pre_save signal to auto-bind organization for AssetEvent.

        Priority: explicit assignment, current tenant, document.organization,
        default organization.
        """
        try:
            from django.db.models.signals import pre_save

            from mayan.apps.analytics.models import AssetEvent

            from .literals import DEFAULT_ORGANIZATION_SLUG
            from .managers import get_current_organization
            from .models import Organization

            def _bind_assetevent_organization(sender, instance, **kwargs):
                if getattr(instance, 'organization_id', None):
                    return

                organization = get_current_organization()

                if organization is None:
                    document = getattr(instance, 'document', None)
                    organization = getattr(
                        document, 'organization', None
                    ) if document else None

                if organization is None:
                    organization = Organization.objects.filter(
                        slug=DEFAULT_ORGANIZATION_SLUG
                    ).first()

                if organization is not None:
                    instance.organization = organization

            pre_save.connect(
                _bind_assetevent_organization,
                sender=AssetEvent,
                dispatch_uid='organizations_bind_assetevent_organization',
                weak=False
            )
            logger.debug('Connected AssetEvent tenant binding signal')
        except Exception as exc:
            logger.warning(
                'Could not connect AssetEvent tenant binding signal: %s', exc
            )

    def _connect_sharelink_tenant_binding_signal(self):
        """
        Connect pre_save signal to auto-bind organization for ShareLink.

        Priority: explicit assignment, current tenant, organization from
        rendition → publication_item → document_file → document, default org.
        Lazy import of ShareLink to avoid circular imports with distribution.
        """
        try:
            from django.db.models.signals import pre_save

            from .literals import DEFAULT_ORGANIZATION_SLUG
            from .managers import get_current_organization
            from .models import Organization

            def _bind_sharelink_organization(sender, instance, **kwargs):
                if getattr(instance, 'organization_id', None):
                    return

                organization = get_current_organization()

                if organization is None:
                    try:
                        rendition = getattr(instance, 'rendition', None)
                        if rendition:
                            pub_item = getattr(
                                rendition, 'publication_item', None
                            )
                            if pub_item:
                                doc_file = getattr(
                                    pub_item, 'document_file', None
                                )
                                if doc_file:
                                    document = getattr(
                                        doc_file, 'document', None
                                    )
                                    if document:
                                        organization = getattr(
                                            document, 'organization', None
                                        )
                    except Exception:
                        pass

                if organization is None:
                    organization = Organization.objects.filter(
                        slug=DEFAULT_ORGANIZATION_SLUG
                    ).first()

                if organization is not None:
                    instance.organization = organization

            from mayan.apps.distribution.models import ShareLink

            pre_save.connect(
                _bind_sharelink_organization,
                sender=ShareLink,
                dispatch_uid='organizations_bind_sharelink_organization',
                weak=False
            )
            logger.debug('Connected ShareLink tenant binding signal')
        except Exception as exc:
            logger.warning(
                'Could not connect ShareLink tenant binding signal: %s', exc
            )

    def _connect_cabinet_tenant_binding_signal(self):
        """
        Connect pre_save signal to auto-bind organization for Cabinet.

        Cabinet.organization is NOT NULL at DB level. API create may not pass
        organization; inject from tenant context before insert.
        """
        try:
            from django.db.models.signals import pre_save

            from mayan.apps.cabinets.models import Cabinet

            from .literals import DEFAULT_ORGANIZATION_SLUG
            from .managers import get_current_organization
            from .models import Organization

            def _bind_cabinet_organization(sender, instance, **kwargs):
                if getattr(instance, 'organization_id', None):
                    return

                organization = get_current_organization()
                if organization is None:
                    organization = Organization.objects.filter(
                        slug=DEFAULT_ORGANIZATION_SLUG
                    ).first()

                if organization is not None:
                    instance.organization = organization

            pre_save.connect(
                _bind_cabinet_organization,
                sender=Cabinet,
                dispatch_uid='organizations_bind_cabinet_organization',
                weak=False
            )
            logger.debug('Connected Cabinet tenant binding signal')
        except Exception as exc:
            logger.warning(
                'Could not connect Cabinet tenant binding signal: %s', exc
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
