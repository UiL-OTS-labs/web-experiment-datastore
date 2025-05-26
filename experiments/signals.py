import sys

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import DataPoint, ParticipantSession, Experiment


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

    if not instance.size or instance.size == 0:
        if instance.data is not None:
            instance.size = sys.getsizeof(instance.data)
        else:
            instance.size = instance.file.size


@receiver(post_delete, sender=DataPoint)
def on_datapoint_delete(sender, instance, *args, **kwargs):
    if instance.session is not None:
        instance.session.delete_if_empty()


@receiver(pre_save, sender=ParticipantSession)
def on_participant_session_creation(
        sender,
        instance: ParticipantSession,
        *args,
        **kwargs):

    # save the state of the experiment at the time the session was started
    instance.experiment_state = instance.experiment.state

    """
    Add an incremental session_id number when saving a session starting from 1
    """
    if not instance.subject_id:
        experiment = instance.experiment
        last_session = experiment.participantsession_set.all().order_by(
            'subject_id'
        ).last()

        if last_session:
            instance.subject_id = last_session.subject_id + 1
        else:
            instance.subject_id = 1


@receiver(post_save, sender=Experiment)
def on_experiment_creation(
        sender,
        instance: Experiment,
        *args,
        **kwargs):
    """Add one default group, with "Default Group" as name"""
    if instance.targetgroup_set.count() == 0:
        instance.targetgroup_set.create(
            name="Default Group",
            completion_target=500
        )
