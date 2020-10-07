from django.utils.functional import cached_property
import braces.views as braces

from experiments.models import Experiment


class ExperimentMixin:
    _experiment_kwargs_key = 'experiment'

    @cached_property
    def experiment(self):
        return Experiment.objects.get(pk=self.kwargs[self._experiment_kwargs_key])


class UserAllowedMixin(braces.LoginRequiredMixin, ExperimentMixin):

    def dispatch(self, request, *args, **kwargs):
        if not self.experiment.users.filter(pk=request.user.pk).exists():
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)
