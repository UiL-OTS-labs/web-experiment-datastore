from django.http import HttpResponseBadRequest, HttpResponseForbidden, Http404
from django.utils.functional import cached_property
from django.views import generic
import braces.views as braces
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy as reverse
from django.conf import settings

from .forms import ExperimentForm
from .models import Experiment, DataPoint
from .utils import create_download_response_zip, create_file_response_single


class ExperimentHomeView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/overview.html'
    model = Experiment

    def get_queryset(self):
        return self.model.objects.filter(users=self.request.user)


class ExperimentCreateView(braces.LoginRequiredMixin, SuccessMessageMixin,
                           generic.CreateView):
    template_name = 'experiments/new.html'
    form_class = ExperimentForm
    success_message = _('experiments:message:create:success')

    def get_success_url(self):
        return reverse('experiments:home')

    def form_valid(self, form):
        # Add current user to users
        experiment = form.save()
        experiment.users.add(self.request.user)
        experiment.save()

        return super().form_valid(form)


class ExperimentDetailView(braces.LoginRequiredMixin, generic.ListView):
    template_name = 'experiments/detail.html'
    model = DataPoint

    @cached_property
    def experiment(self):
        return Experiment.objects.get(pk=self.kwargs['experiment'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context['experiment'] = self.experiment
        context['webexp_host'] = settings.WEBEXPERIMENT_HOST

        return context

    def get_queryset(self):
        return self.model.objects.filter(experiment=self.experiment)


class DownloadView(braces.LoginRequiredMixin, generic.View):
    _formats = ['csv', 'raw']

    def get(self, request, experiment, file_format='csv', data_point=None):
        if file_format not in self._formats:
            return HttpResponseBadRequest()

        # Only allow users that are attached to this experiment
        if not self.experiment.users.filter(
                username=request.user.username
        ).exists():
            return HttpResponseForbidden()

        if data_point:
            qs = self.experiment.datapoint_set.filter(pk=data_point)
            if not qs.exists():
                return Http404()

            return create_file_response_single(file_format, qs.first())
        else:
            return create_download_response_zip(file_format, self.experiment)

    @cached_property
    def experiment(self):
        return Experiment.objects.get(pk=self.kwargs['experiment'])
