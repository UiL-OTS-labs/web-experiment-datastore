from django.contrib.auth.views import redirect_to_login
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
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            redirect_to_login(request.get_full_path(),
                              self.get_login_url(),
                              self.get_redirect_field_name())

        if not self.experiment.users.filter(pk=request.user.pk).exists():
            return self.handle_no_permission(request)

        return super().dispatch(request, *args, **kwargs)
