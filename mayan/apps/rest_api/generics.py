from rest_framework import generics as rest_framework_generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from django.core.exceptions import ImproperlyConfigured

from mayan.apps.dynamic_search.filters import RESTAPISearchFilter

from .api_view_mixins import (
    CheckQuerysetAPIViewMixin, DynamicFieldListAPIViewMixin,
    InstanceExtraDataAPIViewMixin, SerializerExtraContextAPIViewMixin,
    SchemaInspectionAPIViewMixin
)
from .filters import MayanObjectPermissionsFilter, MayanSortingFilter
from .permissions import MayanPermission
from .serializers import BlankSerializer


class GenericAPIView(
    CheckQuerysetAPIViewMixin, SchemaInspectionAPIViewMixin,
    rest_framework_generics.GenericAPIView
):
    filter_backends = (MayanObjectPermissionsFilter,)
    permission_classes = (MayanPermission,)


class CreateAPIView(
    CheckQuerysetAPIViewMixin, InstanceExtraDataAPIViewMixin,
    SchemaInspectionAPIViewMixin, SerializerExtraContextAPIViewMixin,
    rest_framework_generics.CreateAPIView
):
    """
    requires:
        view_permission = {'POST': ...}
    """
    permission_classes = (MayanPermission,)


class ListAPIView(
    CheckQuerysetAPIViewMixin, DynamicFieldListAPIViewMixin,
    SchemaInspectionAPIViewMixin, SerializerExtraContextAPIViewMixin,
    rest_framework_generics.ListAPIView
):
    """
    requires:
        object_permission = {'GET': ...}
    """
    filter_backends = (
        MayanObjectPermissionsFilter, MayanSortingFilter, RESTAPISearchFilter
    )
    # permission_classes is required for the EventListAPIView
    # when Actions objects support ACLs then this can be removed
    # as was intented.
    permission_classes = (MayanPermission,)


class ListCreateAPIView(
    CheckQuerysetAPIViewMixin, DynamicFieldListAPIViewMixin,
    InstanceExtraDataAPIViewMixin, SchemaInspectionAPIViewMixin,
    SerializerExtraContextAPIViewMixin,
    rest_framework_generics.ListCreateAPIView
):
    """
    requires:
        object_permission = {'GET': ...}
        view_permission = {'POST': ...}
    """
    filter_backends = (
        MayanObjectPermissionsFilter, MayanSortingFilter, RESTAPISearchFilter
    )
    permission_classes = (MayanPermission,)


class ObjectActionAPIView(SerializerExtraContextAPIViewMixin, GenericAPIView):
    action_response_status = None
    serializer_class = BlankSerializer

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def object_action(self, serializer):
        raise ImproperlyConfigured(
            '{cls} class needs to specify the `.perform_action()` method.'.format(
                cls=self.__class__.__name__
            )
        )

    def post(self, request, *args, **kwargs):
        return self.view_action(request, *args, **kwargs)

    def view_action(self, request, *args, **kwargs):
        self.object = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if hasattr(self, 'get_instance_extra_data'):
            for key, value in self.get_instance_extra_data().items():
                setattr(self.object, key, value)

        result = self.object_action(request=request, serializer=serializer)

        if result:
            # If object action returned serializer.data.
            headers = self.get_success_headers(data=result)
            return Response(
                headers=headers, data=result,
                status=self.action_response_status or status.HTTP_200_OK
            )
        else:
            return Response(
                status=self.action_response_status or status.HTTP_200_OK
            )


class RetrieveAPIView(
    CheckQuerysetAPIViewMixin, DynamicFieldListAPIViewMixin,
    InstanceExtraDataAPIViewMixin, SchemaInspectionAPIViewMixin,
    SerializerExtraContextAPIViewMixin,
    rest_framework_generics.RetrieveAPIView
):
    """
    requires:
        object_permission = {
            'GET': ...,
        }
    """
    filter_backends = (MayanObjectPermissionsFilter,)


class RetrieveDestroyAPIView(
    CheckQuerysetAPIViewMixin, DynamicFieldListAPIViewMixin,
    InstanceExtraDataAPIViewMixin, SchemaInspectionAPIViewMixin,
    SerializerExtraContextAPIViewMixin,
    rest_framework_generics.RetrieveDestroyAPIView
):
    """
    requires:
        object_permission = {
            'DELETE': ...,
            'GET': ...,
        }
    """
    filter_backends = (MayanObjectPermissionsFilter,)


class RetrieveUpdateAPIView(
    CheckQuerysetAPIViewMixin, DynamicFieldListAPIViewMixin,
    InstanceExtraDataAPIViewMixin, SchemaInspectionAPIViewMixin,
    SerializerExtraContextAPIViewMixin,
    rest_framework_generics.RetrieveUpdateAPIView
):
    """
    requires:
        object_permission = {
            'GET': ...,
            'PATCH': ...,
            'PUT': ...
        }
    """
    filter_backends = (MayanObjectPermissionsFilter,)


class RetrieveUpdateDestroyAPIView(
    CheckQuerysetAPIViewMixin, DynamicFieldListAPIViewMixin,
    InstanceExtraDataAPIViewMixin, SchemaInspectionAPIViewMixin,
    SerializerExtraContextAPIViewMixin,
    rest_framework_generics.RetrieveUpdateDestroyAPIView
):
    """
    requires:
        object_permission = {
            'DELETE': ...,
            'GET': ...,
            'PATCH': ...,
            'PUT': ...
        }
    """
    filter_backends = (MayanObjectPermissionsFilter,)
