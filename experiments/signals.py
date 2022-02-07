from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import DataPoint, ParticipantSession


@receiver(pre_save, sender=DataPoint)
def on_datapoint_creation(sender, instance, *args, **kwargs):
    if not instance.number:
        # Set this DP's number
        experiment = instance.experiment
        last_datapoint = experiment.datapoint_set.all().order_by(
            'date_added'
        ).last()

        if last_datapoint:
            instance.number = last_datapoint.number + 1
        else:
            instance.number = 1


@receiver(pre_save, sender=ParticipantSession)
def on_participant_session_creation(sender, instance, *args, **kwargs):
    """
    Add an incremental session_id number when saving a session starting from 1
    """
    if not instance.subject_id:
        experiment = instance.experiment
        experiment_sessions = experiment.session_set.all()
        new_id = len(experiment_sessions) + 1
        instance.subject_id = new_id

