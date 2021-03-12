from typing import Union

from django.core.exceptions import ObjectDoesNotExist, ValidationError

from experiments.models import Experiment


class ApiExperimentMixin:

    def get_experiment(self, access_id: str) -> Union[Experiment, None]:
        """Tries to get experiment for the given access_id. Returns None if
        it does not exist of it does not pass validation.

        The validation error sometimes happens for unknown reasons...
        """
        try:
            return Experiment.objects.get(access_id=access_id)
        except (ObjectDoesNotExist, ValidationError):
            return None
