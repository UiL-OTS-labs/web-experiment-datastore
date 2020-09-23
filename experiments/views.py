from django.utils.functional import cached_property
from django.views import generic
import braces.views as braces
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy as reverse
from django.conf import settings

from .forms import ExperimentForm
from .models import Experiment, DataPoint


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
