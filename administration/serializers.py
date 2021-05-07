from experiments.serializers import ExperimentSerializer
from experiments.models import Experiment
from rest_framework import serializers
from main.serializers import UserSerializer


class AdminExperimentSerializer(ExperimentSerializer):
    class Meta:
        model = Experiment
        fields = ['pk', 'title', 'users', 'state', 'approved', 'access_id',
                  'folder_name', 'num_datapoints', 'date_created',
                  'show_in_ldap_config', 'last_upload']

    users = serializers.SerializerMethodField()
    last_upload = serializers.SerializerMethodField()

    def get_users(self, experiment):
        return UserSerializer(experiment.users.all(), many=True).data

    def get_last_upload(self, experiment):
        last_dp = experiment.datapoint_set.last()

        if last_dp:
            return last_dp.date_added

        return None
