from typing import Union

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .parsers import PlainTextParser
from experiments.models import DataPoint, Experiment


class UploadView(APIView):
    """This view is used to upload data into an experiment.

    It only accepts plain text content, as otherwise the Django Rest
    Framework tries to force the data into a Python format. Not only is this
    fault intolerant, we want to store the data as raw as possible.

    Raw data doesn't lose resolution, and allows for more flexibility later on.

    This view also checks several things:
    - A valid access key should be used
    - The experiment should be approved
    - The experiment should have the 'OPEN' state

    If any of these conditions are not met, an error should be returned.
    """
    parser_classes = [PlainTextParser]

    def post(self, request, access_key):
        payload = request.data

        # Should not happen(tm), as it's a path variable.
        if not access_key or len(access_key) == 0:
            return Response({
                "result": "ERR_NO_ID",
                "message": "No upload_id was provided"
                },
                status=400  # Bad request
            )

        # Error if no data was sent
        if not payload:
            return Response({
                "result":  "ERR_NO_DATA",
                "message": "No data was provided"
                },
                status=400  # Bad request
            )

        experiment = self.get_experiment(access_key)

        if not experiment:
            return Response({
                "result":  "ERR_UNKNOWN_ID",
                "message": "No experiment using that id was found"
                },
                status=400  # Bad request
            )

        # The experiment should be approved and open.
        if not experiment.state == experiment.OPEN or not experiment.approved:
            return Response({
                "result":  "ERR_NOT_OPEN",
                "message": "The experiment is not open to new uploads"
            },
                status=403  # Forbidden
            )

        # Create the new datapoint
        dp = DataPoint()
        dp.experiment = experiment
        dp.data = payload
        dp.save()

        # Return that everything went OK
        return Response({
            "result":  "OK",
            "message": "Upload successful"
        })

    def get_experiment(self, access_id: str) -> Union[Experiment, None]:
        """Tries to get experiment for the given access_id. Returns None if
        it does not exist of it does not pass validation.

        The validation error sometimes happens for unknown reasons...
        """
        try:
            return Experiment.objects.get(access_id=access_id)
        except (ObjectDoesNotExist, ValidationError):
            return None
