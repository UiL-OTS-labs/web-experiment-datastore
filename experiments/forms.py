from django import forms

from .models import Experiment


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ('title', 'users')
        widgets = {
            'title':         forms.TextInput,
        }