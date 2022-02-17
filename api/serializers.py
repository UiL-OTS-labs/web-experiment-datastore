from rest_framework.serializers import ModelSerializer

from experiments.models import ParticipantSession


class ParticipantSerializer(ModelSerializer):
    class Meta:
        model = ParticipantSession
        fields = ['uuid', 'state', 'group_name', 'subject_id']
