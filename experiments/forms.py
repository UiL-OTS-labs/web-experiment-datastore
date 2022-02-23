from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import Experiment, TargetGroup


class EditExperimentForm(forms.ModelForm):
    """Form to edit an experiment. Differs from the creation form, as it
    does not allow editing of the folder_name, but does allow changing the
    state of the experiment.
    """
    class Meta:
        model = Experiment
        fields = ('title', 'state', 'users',)
        widgets = {
            'title':         forms.TextInput,
            'folder_name':         forms.TextInput,
        }


class CreateExperimentForm(forms.ModelForm):
    """Form to create experiments. Differs from the edit form, as it allows
    changing of the folder_name, but does not have the state field.
    Changing the state at creation is not desired, as we want experiments to
    be explicitly opened by the user when needed.
    """
    class Meta:
        model = Experiment
        fields = ('title', 'folder_name', 'users',)
        widgets = {
            'title':         forms.TextInput,
            'folder_name':         forms.TextInput,
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Adds a new label and help text to folder_name
        self.fields['folder_name'].label = _("experiments:forms:folder_name")
        self.fields['folder_name'].help_text = _(
            "experiments:forms:folder_name:help"
        ).format(settings.WEBEXPERIMENT_HOST)

    def clean_folder_name(self):
        """Ensures that no 2 experiments will have the same folder name"""
        data = self.cleaned_data['folder_name']

        if Experiment.objects.filter(folder_name=data).exists():
            self.add_error(
                'folder_name',
                _('experiments:forms:create:duplicate_folder')
            )

        return data.lower()


class DownloadForm(forms.Form):
    file_format = forms.ChoiceField(widget=forms.RadioSelect,
                                    choices=[('csv', 'CSV'),
                                             ('raw', 'Raw')])
    include_status = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                               choices=[(Experiment.OPEN, 'Test'),
                                                        (Experiment.PILOTING, 'Pilot')])
    include_groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                               choices=())

    def __init__(self, *args, **kwargs):
        experiment = kwargs.pop('experiment')
        super().__init__(*args, **kwargs)
        self.fields['include_groups'].choices = [(tg.pk, tg.name)
                                                 for tg in experiment.targetgroup_set.all()]

        # select all by default
        self.fields['include_status'].initial = [k for k, v in self.fields['include_status'].choices]
        self.fields['include_groups'].initial = [k for k, v in self.fields['include_groups'].choices]
