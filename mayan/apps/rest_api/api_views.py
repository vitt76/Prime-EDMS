from rest_framework import mixins, permissions, renderers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import update_last_login
import logging
from rest_framework.schemas.generators import EndpointEnumerator

import mayan
from mayan.apps.organizations.settings import setting_organization_url_base_path
from mayan.apps.rest_api import generics

from .classes import BatchRequestCollection, Endpoint
from .generics import RetrieveAPIView, ListAPIView
from .serializers import (
    BatchAPIRequestResponseSerializer, EndpointSerializer,
    ProjectInformationSerializer
)


class APIRoot(ListAPIView):
    swagger_schema = None
    serializer_class = EndpointSerializer

    def get_queryset(self):
        """
        get: Return a list of all API root endpoints. This includes the
        API version root and root services.
        """
        endpoint_api_version = Endpoint(
            label='API version root', viewname='rest_api:api_version_root'
        )
        endpoint_openapi_ui = Endpoint(
            label='OpenAPI UI', viewname='rest_api:schema-openapi-ui'
        )
        endpoint_openapi_schema = Endpoint(
            label='OpenAPI schema', viewname='rest_api:schema-openapi'
        )
        return [
            endpoint_api_version,
            endpoint_openapi_ui,
            endpoint_openapi_schema
        ]


class APIVersionRoot(ListAPIView):
    swagger_schema = None
    serializer_class = EndpointSerializer

    def get_queryset(self):
        """
        get: Return a list of the API version resources and endpoint.
        """
        endpoint_enumerator = EndpointEnumerator()

        if setting_organization_url_base_path.value:
            url_index = 4
        else:
            url_index = 3

        # Extract the resource names from the API endpoint URLs
        parsed_urls = set()
        for entry in endpoint_enumerator.get_api_endpoints():
            try:
                url = entry[0].split('/')[url_index]
            except IndexError:
                """An unknown or invalid URL"""
            else:
                parsed_urls.add(url)

        endpoints = []
        for url in sorted(parsed_urls):
            if url:
                endpoints.append(
                    Endpoint(label=url)
                )

        return endpoints


class BatchRequestAPIView(mixins.ListModelMixin, generics.GenericAPIView):
    """
    post: Submit a batch API request.
    """
    serializer_class = BatchAPIRequestResponseSerializer

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        batch_request_collection = BatchRequestCollection(
            request_list=serializer.validated_data.get('requests')
        )
        return batch_request_collection.execute(
            view_request=self.request._request
        )


class BrowseableObtainAuthToken(ObtainAuthToken):
    """
    Obtain an API authentication token.
    """
    renderer_classes = (renderers.BrowsableAPIRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        try:
            update_last_login(sender=None, user=user)
        except Exception as exc:
            logging.getLogger(__name__).warning(
                'Unable to update last_login for user %s: %s', user, exc
            )
        return Response({'token': token.key})


class ProjectInformationAPIView(RetrieveAPIView):
    serializer_class = ProjectInformationSerializer

    def get_object(self):
        return mayan
