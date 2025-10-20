from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured

from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.settings import api_settings

from mayan.apps.databases.utils import check_queryset
from mayan.apps.views.mixins import ExternalObjectBaseMixin

from .literals import (
    QUERY_FIELD_EXCLUDE_PARAMETER, QUERY_FIELD_ONLY_PARAMETER
)


class AsymmetricSerializerAPIViewMixin:
    _write_methods = ('PATCH', 'POST', 'PUT')
    read_serializer_class = None
    write_serializer_class = None

    def get_read_serializer_class(self):
        if not self.read_serializer_class:
            raise ImproperlyConfigured(
                'View {} must specify a read_serializer_class.'.format(
                    self.__class__.__name__
                )
            )
        else:
            return self.read_serializer_class

    def get_serializer_class(self):
        if getattr(self, 'serializer_class', None):
            raise ImproperlyConfigured(
                'View {} can not use AsymmetricSerializerAPIViewMixin while '
                'also specifying a serializer_class.'.format(
                    self.__class__.__name__
                )
            )

        if self.request.method in self._write_methods:
            return self.get_write_serializer_class()
        else:
            return self.get_read_serializer_class()

    def get_write_serializer_class(self):
        if not self.write_serializer_class:
            raise ImproperlyConfigured(
                'View {} must specify a write_serializer_class.'.format(
                    self.__class__.__name__
                )
            )
        else:
            return self.write_serializer_class


class CheckQuerysetAPIViewMixin:
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        return check_queryset(self=self, queryset=queryset)


class ContentTypeAPIViewMixin:
    """
    This mixin makes it easier for API views to retrieve a content type from
    the URL pattern.
    """
    content_type_url_kw_args = {
        'app_label': 'app_label',
        'model_name': 'model_name'
    }

    def get_content_type(self):
        return get_object_or_404(
            queryset=ContentType, app_label=self.kwargs[
                self.content_type_url_kw_args['app_label']
            ], model=self.kwargs[
                self.content_type_url_kw_args['model_name']
            ]
        )


class DynamicFieldListAPIViewMixin:
    def get_serializer_extra_context(self):
        context = super().get_serializer_extra_context()

        if self.request.method == 'GET':
            context.update(
                {
                    'fields_exclude': self.request.query_params.get(
                        QUERY_FIELD_EXCLUDE_PARAMETER, ''
                    ),
                    'fields_only': self.request.query_params.get(
                        QUERY_FIELD_ONLY_PARAMETER, ''
                    )
                }
            )

        return context


class ExternalObjectAPIViewMixin(ExternalObjectBaseMixin):
    """
    Override get_external_object to use REST API get_object_or_404.
    """
    def get_external_object(self):
        return get_object_or_404(
            queryset=self.get_external_object_queryset_filtered(),
            **self.get_pk_url_kwargs()
        )

    def get_external_object_permission(self):
        return getattr(
            self, 'mayan_external_object_permissions', {}
        ).get(self.request.method, (None,))[0]

    def get_serializer_extra_context(self):
        """
        Add the external object to the serializer context. Useful for the
        create action when there is no instance available.
        """
        context = super().get_serializer_extra_context()
        if self.kwargs:
            context['external_object'] = self.external_object

        return context

    def initial(self, *args, **kwargs):
        result = super().initial(*args, **kwargs)
        # Ensure self.external_object is initialized to allow the browseable
        # API view to display when attempting to introspect the serializer
        # and the parent object is not found.
        self.external_object = None

        self.external_object = self.get_external_object()
        return result


class ExternalContentTypeObjectAPIViewMixin(
    ContentTypeAPIViewMixin, ExternalObjectAPIViewMixin
):
    """
    Mixin to retrieve an external object by content type from the URL pattern.
    """
    external_object_pk_url_kwarg = 'object_id'

    def get_external_object_queryset(self):
        self.content_type = self.get_content_type()
        self.external_object_class = self.content_type.model_class()
        return super().get_external_object_queryset()


class InstanceExtraDataAPIViewMixin:
    def perform_create(self, serializer):
        if hasattr(self, 'get_instance_extra_data'):
            serializer.validated_data['_instance_extra_data'] = self.get_instance_extra_data()

        return super().perform_create(serializer=serializer)

    def perform_destroy(self, instance):
        if hasattr(self, 'get_instance_extra_data'):
            for key, value in self.get_instance_extra_data().items():
                setattr(instance, key, value)

        return super().perform_destroy(instance=instance)

    def perform_update(self, serializer):
        if hasattr(self, 'get_instance_extra_data'):
            for key, value in self.get_instance_extra_data().items():
                serializer.validated_data[key] = value

        return super().perform_update(serializer=serializer)


class SchemaInspectionAPIViewMixin:
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return []

        return super().get_queryset()

    def get_serializer(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):

            return None

        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self, *args, **kwargs):
        if getattr(self, 'swagger_fake_view', False):
            return {}

        return super().get_serializer_context(*args, **kwargs)


class SerializerActionAPIViewMixin:
    serializer_action_name = None

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def perform_serializer_action(self, serializer):
        getattr(serializer, self.serializer_action_name)()

    def post(self, request, *args, **kwargs):
        return self.serializer_action(request=request, *args, **kwargs)

    def serializer_action(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_serializer_action(serializer=serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_200_OK, headers=headers
        )


class SerializerExtraContextAPIViewMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(self.get_serializer_extra_context())
        return context

    def get_serializer_extra_context(self):
        return {}


class SuccessHeadersAPIViewMixin:
    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}
