from django.http import Http404
from django.utils import translation
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.serializers import ModelSerializer

from .parsers import PlainTextParser
from experiments.models import DataPoint, Experiment, ParticipantSession


class ResultCodes:
    OK = "OK"
    ERR_NO_ID = "ERR_NO_ID"
    ERR_NO_DATA = "ERR_NO_DATA"
    ERR_UNKNOWN_ID = "ERR_UNKNOWN_ID"
    ERR_NOT_OPEN = "ERR_NOT_OPEN"
    ERR_GROUP_ASSIGN_FAIL = "ERR_GROUP_ASSIGN_FAIL"
    ERR_NO_SESSION = "ERR_NO_SESSION"


class ApiExperimentView(GenericAPIView):
    lookup_field = 'access_id'
    lookup_url_kwarg = 'access_key'
    queryset = Experiment.objects.all()

    def dispatch(self, *args, **kwargs):
        # API responses should always use English messages
        with translation.override('en'):
            return super().dispatch(*args, **kwargs)

    def get_object(self):
        try:
            return super().get_object()
        except Http404 as e:
            # add exception code
            e.code = ResultCodes.ERR_UNKNOWN_ID
            e.detail = 'No experiment using that id was found'
            raise

    @property
    def experiment(self):
        return self.get_object()


def exception_handler(exc, context):
    response = default_exception_handler(exc, context)

    if response:
        if hasattr(exc, 'code'):
            response.data['result'] = exc.code
        if hasattr(exc, 'detail'):
            response.data['message'] = exc.detail

    return response


class MetadataView(ApiExperimentView):
    # List of all variables that are retrievable
    fields = ('state', )

    def get(self, request, access_key, field=None):
        if field in self.fields:
            return Response(self.get_value(self.experiment, field))

        return Response({field: self.get_value(self.experiment, field) for field in self.fields})

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

    def post(self, request, access_key, participant_id=None):
        payload = request.data

        # Error if no data was sent
        if not payload:
            return Response({
                "result":  ResultCodes.ERR_NO_DATA,
                "message": "No data was provided"
            },
                status=400  # Bad request
            )

        # The experiment should be approved and open.
        if not self.experiment.is_open():
            return Response({
                "result":  ResultCodes.ERR_NOT_OPEN,
                "message": "The experiment is not open to new uploads"
            },
                status=403  # Forbidden
            )

        participant = None
        if participant_id:
            participant = self.experiment.participantsession_set\
                                         .get(uuid=participant_id)

        if self.experiment.has_groups() and participant is None:
            # If the experiment is configured to use target groups,
            # then session ids are mandatory
            return Response({
                "result":  ResultCodes.ERR_NO_SESSION,
                "message": "Bad or missing participant session id"
            }, status=403)

        # Create the new datapoint
        dp = DataPoint()
        dp.experiment = self.experiment
        dp.data = payload

        if participant:
            dp.session = participant
        dp.save()

        if participant:
            participant.complete()

        # Return that everything went OK
        return Response({
            "result":  ResultCodes.OK,
            "message": "Upload successful"
        })


class ParticipantSerializer(ModelSerializer):
    class Meta:
        model = ParticipantSession
        fields = ['uuid', 'state', 'group_name']


class ParticipantView(ApiExperimentView, CreateAPIView):
    serializer_class = ParticipantSerializer

    def create(self, *args, **kwargs):
        """creates a new participant session"""
        if not self.experiment.is_open():
            return Response({
                "result":  ResultCodes.ERR_NOT_OPEN,
                "message": "The experiment is not open to new uploads"
            },
                status=403  # Forbidden
            )

        group = self.experiment.assign_to_group()
        if not group:
            return Response({
                'result': ResultCodes.ERR_GROUP_ASSIGN_FAIL,
                'message': 'Could not assign participant to any group',
            },
                status=400
            )

        participant = ParticipantSession.objects.create(
            experiment=self.experiment,
            state=ParticipantSession.STARTED,
            group=group
        )

        serialized = self.serializer_class(participant)
        return Response(serialized.data)
