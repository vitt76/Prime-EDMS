from mayan.apps.rest_api import generics
from mayan.apps.rest_api.api_view_mixins import ExternalObjectAPIViewMixin

from ..models import Recipient, RecipientList
from ..permissions import permission_recipient_api_manage
from ..serializers import RecipientSerializer, RecipientListSerializer


class APIRecipientListView(generics.ListCreateAPIView):
    """
    get: Return a list of recipients.
    post: Create a new recipient.
    """
    mayan_object_permissions = {'GET': (permission_recipient_api_manage,)}
    mayan_view_permissions = {'POST': (permission_recipient_api_manage,)}
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIRecipientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a recipient.
    put: Edit the properties of a recipient.
    patch: Edit the properties of a recipient.
    delete: Delete a recipient.
    """
    mayan_object_permissions = {
        'GET': (permission_recipient_api_manage,),
        'PUT': (permission_recipient_api_manage,),
        'PATCH': (permission_recipient_api_manage,),
        'DELETE': (permission_recipient_api_manage,)
    }
    queryset = Recipient.objects.all()
    serializer_class = RecipientSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIRecipientListListView(generics.ListCreateAPIView):
    """
    get: Return a list of recipient lists.
    post: Create a new recipient list.
    """
    mayan_object_permissions = {'GET': (permission_recipient_api_manage,)}
    mayan_view_permissions = {'POST': (permission_recipient_api_manage,)}
    queryset = RecipientList.objects.all()
    serializer_class = RecipientListSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIRecipientListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a recipient list.
    put: Edit the properties of a recipient list.
    patch: Edit the properties of a recipient list.
    delete: Delete a recipient list.
    """
    mayan_object_permissions = {
        'GET': (permission_recipient_api_manage,),
        'PUT': (permission_recipient_api_manage,),
        'PATCH': (permission_recipient_api_manage,),
        'DELETE': (permission_recipient_api_manage,)
    }
    queryset = RecipientList.objects.all()
    serializer_class = RecipientListSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }
