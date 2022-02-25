# Generated by Django 3.2.11 on 2022-02-23 12:25

from django.db import migrations, models
import django.db.models.deletion

from experiments.models import ParticipantSession

def participant_session_assign_default_group(apps, schema_editor):
    """
    There might be ParticipantSession 's with group=null.
    This code will add the first group from the experiment.
    """
    psession : ParticipantSession = apps.get_model("experiments", "ParticipantSession")
    for session in psession.objects.filter(group=None):
        experiment = session.experiment
        if experiment.targetgroup_set.count() == 0:
            experiment.save()  # Ensure a default group via signal's.
        if experiment.targetgroup_set.count() > 1: # should not happen
            raise ValueError(
                "We assume there is one group, this script can't choose"
            )
        session.group = experiment.targetgroup_set.first()
        session.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0012_auto_20220208_1320'),
    ]

    operations = [
        migrations.RunPython(
            participant_session_assign_default_group
        ),
        migrations.AlterField(
            model_name='participantsession',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='experiments.targetgroup'),
        )
    ]
