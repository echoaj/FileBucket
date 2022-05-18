from django import forms
from .models import Info


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        # name of field for form: Example: form.file
        fields = ('file',)

        # adding attributes to the invisible form.file upload btn with in view
        attributes = {
            "style": "display: none;",
            "id": "file-choose",
            "method": "post",
            "enctype": "multipart/form-data"
        }

        # setting the attributes
        widgets = {
            'file': forms.FileInput(attrs=attributes),
        }
