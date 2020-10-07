from typing import Union

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .parsers import PlainTextParser
from experiments.models import DataPoint, Experiment

class UploadView(APIView):
    parser_classes = [PlainTextParser]

    def post(self, request, access_key):
        payload = request.data

        # Should not happen, as it's a path variable. BBSTS
        if not access_key or len(access_key) == 0:
            return Response({
                "result": "ERR_NO_ID",
                "message": "No upload_id was provided"
                },
                status=400  # Bad request
            )

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

        if not experiment.state == experiment.OPEN:
            return Response({
                "result":  "ERR_NOT_OPEN",
                "message": "The experiment is not open to new uploads"
            },
                status=403  # Forbidden
            )

        dp = DataPoint()
        dp.experiment = experiment
        dp.data = payload
        dp.save()

        return Response({
            "result":  "OK",
            "message": "Upload successful"
        })

    def get_experiment(self, access_id: str) -> Union[Experiment, None]:
        try:
            return Experiment.objects.get(access_id=access_id)
        except (ObjectDoesNotExist, ValidationError):
            return None
