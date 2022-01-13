from django.utils import translation
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import ApiExperimentMixin
from .parsers import PlainTextParser
from experiments.models import DataPoint, Experiment


class ApiExperimentView(ApiExperimentMixin, APIView):
    def dispatch(self, *args, **kwargs):
        # API responses should always use English messages
        with translation.override('en'):
            return super().dispatch(*args, **kwargs)


class MetadataView(ApiExperimentView):

    # List of all variables that are retrievable
    fields = ('state', )

    def get(self, request, access_key, field=None):

        # Should not happen(tm), as it's a path variable.
        if not access_key or len(access_key) == 0:
            return Response({
                "result": "ERR_NO_ID",
                "message": "No access key was provided"
            },
                status=400  # Bad request
            )

        experiment = self.get_experiment(access_key)

        if not experiment:
            return Response({
                "result":  "ERR_UNKNOWN_ID",
                "message": "No experiment using that id was found"
                },
                status=404  # Not found
            )

        if field in self.fields:
            return Response(self.get_value(experiment, field))

        return Response({field: self.get_value(experiment, field) for field in self.fields})

    @staticmethod
    def get_value(experiment: Experiment, field):
        methods = dir(experiment)
        try:
            method = "get_{}_display".format(field)
            # If this field has an explicit display method, use that
            if method in methods:
                return getattr(experiment, method)()
            else:
                # Otherwise, just get the value
                return getattr(experiment, field)
        except AttributeError:
            return None


class UploadView(ApiExperimentView):
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
                "message": "No access key was provided"
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
                status=404  # Not found
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
