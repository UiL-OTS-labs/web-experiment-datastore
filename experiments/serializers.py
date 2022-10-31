from cdh.rest.server.serializers import ModelDisplaySerializer
from .models import Experiment
from rest_framework import serializers


class ExperimentSerializer(ModelDisplaySerializer):
    class Meta:
        model = Experiment
        fields = ['pk', 'title', 'state', 'approved', 'access_id',
                  'folder_name', 'num_datapoints', 'date_created']

    num_datapoints = serializers.SerializerMethodField()

    def get_num_datapoints(self, experiment):
        return experiment.datapoint_set.count()
