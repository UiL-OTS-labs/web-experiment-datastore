from typing import Union

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from experiments.models import DataPoint, Experiment


class ShowDataView(APIView):

    def get(self, request, pk):
        print(pk)
        dp = DataPoint.objects.get(pk=pk)

        return Response(dp.data)


class UploadView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        payload = request.data
        print(payload)

        if 'upload_id' not in payload:
            return Response({
                "result": "ERR_NO_ID",
                "message": "No upload_id was provided"
                },
                status=400
            )

        if 'data' not in payload:
            return Response({
                "result":  "ERR_NO_DATA",
                "message": "No data was provided"
                },
                status=400
            )

        experiment = self.get_experiment(payload.get('upload_id'))

        if not experiment:
            return Response({
                "result":  "ERR_UNKNOWN_ID",
                "message": "No experiment using that id was found"
                },
                status=400
            )

        dp = DataPoint()
        dp.experiment = experiment
        dp.data = payload.get('data')
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
