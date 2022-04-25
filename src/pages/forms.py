from django import forms
from .models import Info


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ('file',)

        attributes = {
            "style": "display: none;",
            "id": "file-choose",
            "method": "post",
            "enctype": "multipart/form-data"
        }

        widgets = {
            'file': forms.FileInput(attrs=attributes),
        }
