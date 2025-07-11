from typing import Dict, Any

from django import forms
from django.http import HttpResponseBadRequest, Http404, HttpResponseRedirect
from django.views import generic
import braces.views as braces
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy as reverse
from django.conf import settings
from rest_framework.authentication import SessionAuthentication

from auditlog.enums import Event, UserType
from auditlog.utils.log import log

from .forms import CreateExperimentForm, EditExperimentForm, DownloadForm
from .models import Experiment, DataPoint, TargetGroup
from .serializers import ExperimentSerializer
from .utils import create_download_response_zip, create_file_response_single, \
    send_new_experiment_mail
from .mixins import UserAllowedMixin


class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    """Overview of all experiments of the current user"""
    template_name = 'experiments/overview.html'
    paginate_by = 10

    def get_queryset(self):
        qs = Experiment.objects.filter(users=self.request.user)
        if 'search' in self.request.GET:
            qs = qs.filter(title__icontains=self.request.GET['search'])

        order_by = '-date_created'
        if self.request.GET.get('sort') == 'date_created':
            order_by = 'date_created'

        qs = qs.order_by(order_by)
        return qs



class ExperimentCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.CreateView):
    """Creation view for new experiments"""
    template_name = 'experiments/new.html'
    form_class = CreateExperimentForm
    success_message = _('experiments:message:create:success')

    def get_success_url(self):
        return reverse('experiments:detail', args=[self.object.pk])

    def get_initial(self):
        """Sets initial user to current User"""
        initial = super().get_initial()
        initial['users'] = [self.request.user]
        return initial

    def form_valid(self, form):
        # Add current user to users
        experiment = form.save()

        if not experiment.users.filter(pk=self.request.user.pk).exists():
            experiment.users.add(self.request.user)
            experiment.save()

        log(
            Event.ADD_DATA,
            "Created experiment {} ({})".format(
                experiment.title,
                experiment.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        send_new_experiment_mail(experiment, self.request.user, self.request)

        return super().form_valid(form)


class ExperimentEditView(UserAllowedMixin, SuccessMessageMixin,
                         generic.UpdateView):
    """Edit view for experiments"""
    template_name = 'experiments/edit.html'
    form_class = EditExperimentForm
    model = Experiment
    success_message = _('experiments:message:edit:success')
    _experiment_kwargs_key = 'pk'
    target_group_formset = forms.inlineformset_factory(
        Experiment,
        TargetGroup,
        fields=('name', 'completion_target'),
        can_delete=False,
        extra=4
    )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['target_group_formset'] = kwargs.get(
            'target_group_formset',
            self.target_group_formset(instance=self.get_object())
        )

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        formset = self.target_group_formset(request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        elif not form.is_valid():
            return self.form_invalid(form)

        return self.render_to_response(
            self.get_context_data(
                form=form,
                target_group_formset=formset
            )
        )

    def get_success_url(self):
        return reverse('experiments:detail', args=[self.object.pk])

    def form_valid(self, form, formset):
        # Add current user to users
        experiment = form.save()
        formset.save()

        if not experiment.users.filter(pk=self.request.user.pk).exists():
            experiment.users.add(self.request.user)
            experiment.save()

        log(
            Event.MODIFY_DATA,
            "Edited experiment {} ({})".format(
                experiment.title,
                experiment.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        return super().form_valid(form)


class ExperimentDetailView(UserAllowedMixin, generic.ListView):
    """Detail view for an experiment.

    Uses a ListView instead of DetailView, as this allows use easier access to
    the DataPoints in this experiment. The experiment is added manually to the
    context.
    """
    template_name = 'experiments/detail.html'
    model = DataPoint

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['experiment'] = self.experiment
        context['webexp_host'] = settings.WEBEXPERIMENT_HOST
        context['webexp_webdav_host'] = settings.WEBEXPERIMENT_WEBDAV_HOST

        return context

    def get_queryset(self):
        return self.model.objects.filter(experiment=self.experiment).defer('data')


class DeleteExperimentView(UserAllowedMixin, SuccessMessageMixin,
                           generic.DeleteView):
    """View to delete an entire experiment"""
    model = Experiment
    _experiment_kwargs_key = 'pk'
    template_name = 'experiments/delete_experiment.html'
    success_message = _('experiments:message:delete:success')

    def form_valid(self, form):
        object = self.get_object()
        log(
            Event.DELETE_DATA,
            "Deleted experiment {} ({})".format(
                object.title,
                object.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('experiments:home')


class DeleteDataPointView(UserAllowedMixin, SuccessMessageMixin,
                          generic.DeleteView):
    """DeleteView for a single DataPoint"""
    model = DataPoint
    template_name = 'experiments/delete_datapoint.html'
    success_message = _('experiments:message:delete_datapoint:success')

    def form_valid(self, form):
        log(
            Event.DELETE_DATA,
            "Deleted datapoint {} from experiment {} ({})".format(
                self.get_object().pk,
                self.experiment.title,
                self.experiment.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['experiment'] = self.experiment

        return context

    def get_success_url(self):
        return reverse('experiments:detail', args=[self.experiment.pk])


class DeleteAllDataView(UserAllowedMixin, SuccessMessageMixin,
                        generic.TemplateView):
    """View to delete all data in an experiment.

    It does not use DeleteView, as that base class cannot do bulk deletions.
    Instead, we use the TemplateView's get method to render a template
    containing a confirmation form. This form triggers the post method, which
    deletes the data and redirects back to the experiment detail view.
    """
    template_name = 'experiments/delete_all_data.html'
    success_message = _('experiments:message:delete_all_data:success')

    def post(self, request, experiment):
        self.experiment.datapoint_set.all().delete()

        log(
            Event.DELETE_DATA,
            "Deleted all data from experiment {} ({})".format(
                self.experiment.title,
                self.experiment.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['experiment'] = self.experiment

        return context

    def get_success_url(self):
        return reverse('experiments:detail', args=[self.experiment.pk])


class DownloadView(UserAllowedMixin, generic.View):
    """View that downloads single, or all data in either CSV or Raw format

    The decision whether to download a single or all data is made by checking
    if a datapoint ID was provided.
    """
    _formats = ['csv', 'raw']

    def get(self, request, experiment, file_format='csv', data_point=None):
        if file_format not in self._formats:
            return HttpResponseBadRequest()

        subject = "all data"
        if data_point:
            subject = "datapoint {}".format(data_point)

        # log action to auditlog
        log(
            Event.DOWNLOAD_DATA,
            "Downloaded {} from experiment {} ({})".format(
                subject,
                self.experiment.title,
                self.experiment.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        if data_point:
            qs = self.experiment.datapoint_set.filter(pk=data_point)
            if not qs.exists():
                return Http404()

            return create_file_response_single(file_format, qs.first())
        else:
            return create_download_response_zip(file_format, self.experiment)


class DownloadFormView(UserAllowedMixin, generic.FormView):
    form_class = DownloadForm
    template_name = 'experiments/download.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['experiment'] = self.experiment
        return kwargs

    def form_valid(self, form):
        file_format = form.cleaned_data['file_format']
        queryset = self.experiment.datapoint_set \
            .filter(session__experiment_state__in=form.cleaned_data['include_status']) \
            .filter(session__group__in=form.cleaned_data['include_groups']).defer('data')
        return create_download_response_zip(file_format, self.experiment, queryset)
