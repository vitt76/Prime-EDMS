from mayan.apps.rest_api import generics

from ..models import RenditionPreset
from ..permissions import permission_preset_api_manage
from ..serializers import RenditionPresetSerializer


class APIRenditionPresetListView(generics.ListCreateAPIView):
    """
    get: Return a list of rendition presets.
    post: Create a new rendition preset.
    """
    mayan_object_permissions = {'GET': (permission_preset_api_manage,)}
    mayan_view_permissions = {'POST': (permission_preset_api_manage,)}
    queryset = RenditionPreset.objects.all()
    serializer_class = RenditionPresetSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class APIRenditionPresetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    get: Return the details of a rendition preset.
    put: Edit the properties of a rendition preset.
    patch: Edit the properties of a rendition preset.
    delete: Delete a rendition preset.
    """
    mayan_object_permissions = {
        'GET': (permission_preset_api_manage,),
        'PUT': (permission_preset_api_manage,),
        'PATCH': (permission_preset_api_manage,),
        'DELETE': (permission_preset_api_manage,)
    }
    queryset = RenditionPreset.objects.all()
    serializer_class = RenditionPresetSerializer

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }
