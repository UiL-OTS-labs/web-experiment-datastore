from django.http import HttpResponseBadRequest, HttpResponseForbidden, Http404, \
    HttpResponseRedirect
from django.views import generic
import braces.views as braces
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy as reverse
from django.conf import settings

from auditlog.enums import Event, UserType
from auditlog.utils.log import log
from uil.core.views.mixins import DeleteSuccessMessageMixin

from .forms import CreateExperimentForm, EditExperimentForm
from .models import Experiment, DataPoint
from .utils import create_download_response_zip, create_file_response_single, \
    send_new_experiment_mail
from .mixins import UserAllowedMixin


class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/overview.html'
    model = Experiment

    def get_queryset(self):
        return self.model.objects.filter(users=self.request.user)


class ExperimentCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.CreateView):
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
    template_name = 'experiments/edit.html'
    form_class = EditExperimentForm
    model = Experiment
    success_message = _('experiments:message:edit:success')
    _experiment_kwargs_key = 'pk'

    def get_success_url(self):
        return reverse('experiments:detail', args=[self.object.pk])

    def form_valid(self, form):
        # Add current user to users
        experiment = form.save()

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
    template_name = 'experiments/detail.html'
    model = DataPoint

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['experiment'] = self.experiment
        context['webexp_host'] = settings.WEBEXPERIMENT_HOST
        context['webexp_webdav_host'] = settings.WEBEXPERIMENT_WEBDAV_HOST

        return context

    def get_queryset(self):
        return self.model.objects.filter(experiment=self.experiment)


class DeleteExperimentView(UserAllowedMixin, DeleteSuccessMessageMixin,
                           generic.DeleteView):
    model = Experiment
    _experiment_kwargs_key = 'pk'
    template_name = 'experiments/delete_experiment.html'
    success_message = _('experiments:message:delete:success')

    def delete(self, request, *args, **kwargs):
        log(
            Event.DELETE_DATA,
            "Deleted experiment {} ({})".format(
                self.object.title,
                self.object.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('experiments:home')


class DeleteDataPointView(UserAllowedMixin, DeleteSuccessMessageMixin,
                          generic.DeleteView):
    model = DataPoint
    template_name = 'experiments/delete_experiment.html'
    success_message = _('experiments:message:delete_datapoint:success')

    def delete(self, request, *args, **kwargs):
        log(
            Event.DELETE_DATA,
            "Deleted datapoint {} from experiment {} ({})".format(
                self.object.pk,
                self.experiment.title,
                self.experiment.pk
            ),
            self.request.user,
            UserType.RESEARCHER
        )

        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['experiment'] = self.experiment

        return context

    def get_success_url(self):
        return reverse('experiments:detail', args=[self.experiment.pk])


class DeleteAllDataView(UserAllowedMixin, SuccessMessageMixin,
                        generic.TemplateView):
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
    _formats = ['csv', 'raw']

    def get(self, request, experiment, file_format='csv', data_point=None):
        if file_format not in self._formats:
            return HttpResponseBadRequest()

        # Only allow users that are attached to this experiment
        if not self.experiment.users.filter(
                username=request.user.username
        ).exists():
            return HttpResponseForbidden()

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
