from django.utils.functional import cached_property
import braces.views as braces

from experiments.models import Experiment


class ExperimentMixin:
    """Adds a field to the object called 'experiment', which is implemented
    by a cached_property which retrieves the experiment.

    Using a cached property allows us to minimize databases calls in a
    convenient way.
    """
    _experiment_kwargs_key = 'experiment'

    @cached_property
    def experiment(self):
        return Experiment.objects.get(pk=self.kwargs[self._experiment_kwargs_key])


class UserAllowedMixin(braces.LoginRequiredMixin, ExperimentMixin):
    """Extension of the LoginRequiredMixin which also checks if the users is
    allowed to view this experiment.
    """

    def dispatch(self, request, *args, **kwargs):
        if not self.experiment.users.filter(pk=request.user.pk).exists():
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)
