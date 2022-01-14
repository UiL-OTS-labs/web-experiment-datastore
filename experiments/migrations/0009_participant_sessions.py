# Generated by Django 3.2.9 on 2022-01-14 15:51

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0008_auto_20210312_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='TargetGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='experiments:models:targetgroup:name:help', max_length=100, verbose_name='experiments:models:targetgroup:name')),
                ('completed', models.PositiveIntegerField(default=0, help_text='experiments:models:targetgroup:completed:help', verbose_name='experiments:models:targetgroup:completed')),
                ('completion_target', models.IntegerField(help_text='experiments:models:targetgroup:completion_target:help', verbose_name='experiments:models:targetgroup:completion_target')),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.experiment')),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='experiments:models:participant:uuid')),
                ('state', models.PositiveIntegerField(choices=[(1, 'experiments:models:participant:state:started'), (2, 'experiments:models:participant:state:completed'), (3, 'experiments:models:participant:state:rejected')], default=1, help_text='experiments:models:participant:state:help', verbose_name='experiments:models:participant:state')),
                ('experiment_state', models.PositiveIntegerField(null=True)),
                ('date_started', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.experiment')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='experiments.targetgroup')),
            ],
        ),
        migrations.AddField(
            model_name='datapoint',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='experiments.participantsession'),
        ),
    ]
