from django import forms

class UploadFileForm(forms.Form):
    text = forms.CharField(max_length=500)
    file = forms.FileField(required=False)