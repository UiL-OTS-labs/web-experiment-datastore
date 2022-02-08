from django.http import Http404
from django.utils import translation
from functools import cached_property
from rest_framework.exceptions import APIException, ValidationError, PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView

from .exceptions import ConfigError
from .parsers import PlainTextParser
from .serializers import ParticipantSerializer
from experiments.models import DataPoint, Experiment, ParticipantSession


class ResultCodes:
    OK = "OK"
    ERR_NO_ID = "ERR_NO_ID"
    ERR_NO_DATA = "ERR_NO_DATA"
    ERR_UNKNOWN_ID = "ERR_UNKNOWN_ID"
    ERR_NOT_OPEN = "ERR_NOT_OPEN"
    ERR_GROUP_ASSIGN_FAIL = "ERR_GROUP_ASSIGN_FAIL"
    ERR_NO_SESSION = "ERR_NO_SESSION"


class BaseExperimentApiView(GenericAPIView):
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
        except Http404:
            raise NotFound(code=ResultCodes.ERR_UNKNOWN_ID,
                           detail='No experiment using that id was found')

    @cached_property
    def experiment(self):
        return self.get_object()


class MetadataView(BaseExperimentApiView):
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


class BaseUploadView(BaseExperimentApiView):
    """Base view for uploading data into an experiment.

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

    def _validate_request(self, payload):
        # Error if no data was sent
        if not payload:
            raise APIException(code=ResultCodes.ERR_NO_DATA, detail='No data was provided')

        # The experiment should be approved and open.
        if not self.experiment.is_open():
            raise PermissionDenied(code=ResultCodes.ERR_NOT_OPEN,
                                   detail='The experiment is not open to new uploads')

    def _save_data_point(self, payload, session: ParticipantSession):
        dp = DataPoint()
        dp.experiment = self.experiment
        dp.data = payload
        dp.session = session
        dp.save()

        return dp


class UploadView(BaseUploadView):

    def post(self, request, access_key):
        payload = request.data
        self._validate_request(payload)

        if self.experiment.has_groups():
            # If the experiment is configured to use target groups,
            # then session ids are mandatory
            raise ConfigError(code=ResultCodes.ERR_NO_SESSION,
                              detail='Missing participant session id')

        session = ParticipantSession.objects.create(experiment=self.experiment)
        session.complete()

        dp = self._save_data_point(payload, session)

        return Response({
            'result': ResultCodes.OK,
            'message': 'Upload successful'
        })


class SessionUploadView(BaseUploadView):

    def post(self, request, access_key, participant_id):
        payload = request.data
        self._validate_request(payload)

        if not self.experiment.has_groups():
            raise ValidationError(detail='Experiment is not using session ids')

        try:
            participant = self.experiment.participantsession_set\
                                         .get(uuid=participant_id)
        except ParticipantSession.DoesNotExist:
            raise PermissionDenied(code=ResultCodes.ERR_NO_SESSION,
                                   detail='Bad participant session id')

        # Create the new datapoint
        dp = self._save_data_point(payload, participant)

        participant.complete()

        # Return that everything went OK
        return Response({
            "result":  ResultCodes.OK,
            "message": "Upload successful"
        })


class ParticipantView(BaseExperimentApiView, CreateAPIView):
    serializer_class = ParticipantSerializer

    def create(self, *args, **kwargs):
        """creates a new participant session"""
        if not self.experiment.is_open():
            raise PermissionDenied(code=ResultCodes.ERR_NOT_OPEN,
                                   detail="The experiment is not open to new uploads")

        group = self.experiment.get_next_group()
        if not group:
            raise ConfigError(code=ResultCodes.ERR_GROUP_ASSIGN_FAIL,
                              detail='Could not assign participant to any group')

        participant = ParticipantSession.objects.create(
            experiment=self.experiment,
            state=ParticipantSession.STARTED,
            group=group
        )

        serialized = self.serializer_class(participant)
        return Response(serialized.data)
