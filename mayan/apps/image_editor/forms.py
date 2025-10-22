from django import forms


class ImageEditorSaveForm(forms.Form):
    image_content = forms.FileField()
    action_id = forms.CharField(max_length=64, required=False)
    comment = forms.CharField(max_length=255, required=False)
