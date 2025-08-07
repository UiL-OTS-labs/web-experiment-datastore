from rest_framework import serializers
from .models import Experiment



class ExperimentSerializer(serializers.ModelSerializer):
    get_state_display = serializers.CharField(read_only=True)
    users = serializers.SerializerMethodField()
    num_datapoints = serializers.SerializerMethodField()

    class Meta:
        model = Experiment
        fields = [
            'pk', 'title', 'state', 'approved', 'access_id',
            'folder_name', 'num_datapoints', 'date_created',
            'users', 'get_state_display'
        ]

    def get_users(self, experiment):
        return [user.get_full_name() or user.username for user in experiment.users.all()]

    def get_num_datapoints(self, experiment):
        return experiment.datapoint_set.count()

