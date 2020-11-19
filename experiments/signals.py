from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import DataPoint


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
