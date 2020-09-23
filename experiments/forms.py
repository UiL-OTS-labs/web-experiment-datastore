from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('title', 'folder_name')
        widgets = {
            'title':         forms.TextInput,
            'folder_name':         forms.TextInput,
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fields['folder_name'].label = _("experiments:forms:folder_name")
        self.fields['folder_name'].help_text = _(
            "experiments:forms:folder_name:help"
        ).format(settings.WEBEXPERIMENT_HOST)
