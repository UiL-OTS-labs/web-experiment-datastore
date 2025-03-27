from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from cdh.core.fields import EncryptedTextField

from main.models import User


class Experiment(models.Model):
    """Describes the metadata of an experiment"""
    OPEN = 1
    CLOSED = 2
    PILOTING = 3
    STATES = (
        (OPEN, _("experiments:models:experiment:state:open")),
        (CLOSED, _("experiments:models:experiment:state:closed")),
        (PILOTING, _("experiments:models:experiment:state:piloting")),
    )

    # As using UUID's as PK has some annoying implications, we just add it as
    # a separate field.
    access_id = models.UUIDField(
        _("experiments:models:experiment:access_id"),
        unique=True,
        default=uuid.uuid4,
        editable=False
    )

    # All users with access to this experiment
    users = models.ManyToManyField(
        User,
        verbose_name=_("experiments:models:experiment:users"),
        help_text=_("experiments:models:experiment:users:help"),
    )

    # The desired folder name on the hosting server
    folder_name = models.TextField(
        _("experiments:models:experiment:folder_name"),
        validators=[
            RegexValidator(r"^[a-zA-Z0-9\-_]*$")
        ]
    )

    # The human readable name of the experiment
    title = models.TextField(
        _("experiments:models:experiment:title"),
    )

    # Open or closed
    state = models.PositiveIntegerField(
        _("experiments:models:experiment:state"),
        help_text=_("experiments:models:experiment:state:help"),
        choices=STATES,
        default=CLOSED
    )

    date_created = models.DateTimeField(
        _("experiments:models:experiment:date_created"),
        auto_now_add=True
    )

    # Experiments should be approved by staff before it can be used
    approved = models.BooleanField(
        _("experiments:models:experiment:approved"),
        default=False,
    )

    # Used to exclude experiments from the Apache config
    show_in_ldap_config = models.BooleanField(
        _("experiments:models:experiment:show_in_ldap_config"),
        default=True,
    )

    def get_state_display(self):
        # While not included, this is actually a state. One that overrides the
        # state defined by researchers. That is also the reason why it's not
        # a state itself, because it's a hassle to make sure researchers cannot
        # override the 'awaiting approval' state.
        if not self.approved:
            return _('experiments:detail:awaiting_approval')
        else:
            for id, text in self.STATES:
                if id == self.state:
                    return text

        # Should(TM) not happen
        return "<UNKNOWN>"

    def __str__(self):
        return self.title

    def is_open(self):
        """An experiment is open if it is both approved and set to 'open'.
        It should also have at least one target group that is open to new participants.
        While an experiment should not be able to have the status 'open' without being approved,
        we check both to be sure."""
        experiment_open = self.state in (self.OPEN, self.PILOTING) and self.approved
        groups_open = True
        if self.uses_groups():
            groups_open = any((group.is_open() for group in self.targetgroup_set.all()))

        return experiment_open and groups_open

    def uses_groups(self):
        """
        An experiment is designed to use groups when it has more than one group.
        """
        return self.targetgroup_set.count() > 1

    def get_next_group(self):
        # the basic idea here is to assign incoming sessions equally across all available groups.
        # however, since opened session don't necessarily reflect completed sessions, we also try
        # to rebalance the distribution whenever a session is completed
        groups = list(self.targetgroup_set.all().order_by('pk'))
        filtered_sessions = self.participantsession_set.filter(experiment_state=self.state)

        if len(groups) < 1:
            # experiment has no groups defined, it should still be possible to run it using the old API
            # but trying to create a participant session should fail.
            return None

        last_opened = filtered_sessions.order_by('-date_started').first()
        last_closed = filtered_sessions\
            .filter(state=ParticipantSession.COMPLETED)\
            .order_by('-date_updated').first()

        if last_closed is not None and last_closed.date_updated > last_opened.date_started:
            # last thing to happen was a session being completed
            # assign the incoming participant to the group with less completed sessions
            completed_expr = models.Count(
                'participantsession',
                filter=models.Q(participantsession__state=ParticipantSession.COMPLETED,
                                participantsession__experiment_state=self.state)
            )
            annotated = self.targetgroup_set.annotate(completed=completed_expr)
            for group in annotated.order_by('completed'):
                if group.is_open():
                    return group
            return None
        else:
            # last thing to happen was a new session being opened
            # assign the incoming participant to the next group in line
            if last_opened is None:
                # no participants yet
                last_idx = len(groups) - 1
            else:
                last_idx = groups.index(last_opened.group)
            i = (last_idx + 1) % len(groups)
            while not groups[i].is_open():
                # too many completed sessions, advance to the next group
                if i == last_idx:
                    # looped around, no group to assign
                    return None
                i = (i + 1) % len(groups)

            return groups[i]


class DataPoint(models.Model):
    """Model to hold data from a participant in an experiment"""
    class Meta:
        unique_together = ['experiment', 'number']

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    # Counter of the amount of DP's in an experiment
    # Used to display an incrementing ID, independent from other experiments
    number = models.PositiveIntegerField(null=False)

    size = models.PositiveBigIntegerField(
        _("experiments:models:datapoint:size"),
        null=False,
    )

    # Encrypted field for extra security
    data = EncryptedTextField(
        _("experiments:models:datapoint:data"),
    )

    date_added = models.DateTimeField(
        _("experiments:models:datapoint:date_added"),
        auto_now_add=True
    )

    def __str__(self):
        return "Datapoint {}".format(self.number)

    session = models.ForeignKey(
        'ParticipantSession', on_delete=models.CASCADE, null=True)

    STATUS_TEST = _('experiments:models:datapoint:label:test')
    STATUS_PILOT = _('experiments:models:datapoint:label:pilot')

    def get_status_display(self):
        if self.session is None:
            return self.STATUS_TEST
        if self.session.experiment_state == Experiment.PILOTING:
            return self.STATUS_PILOT
        return self.STATUS_TEST


class ParticipantSession(models.Model):
    STARTED = 1
    COMPLETED = 2
    REJECTED = 3
    STATES = (
        (STARTED, _("experiments:models:participant:state:started")),
        (COMPLETED, _("experiments:models:participant:state:completed")),
        (REJECTED, _("experiments:models:participant:state:rejected")),
    )

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    uuid = models.UUIDField(_("experiments:models:participant:uuid"),
                            unique=True, default=uuid.uuid4, editable=False)
    state = models.PositiveIntegerField(
        _("experiments:models:participant:state"),
        choices=STATES,
        default=STARTED
    )
    experiment_state = models.PositiveIntegerField(null=True)

    group = models.ForeignKey(
        'TargetGroup',
        verbose_name=_('experiments:models:participant:group'),
        on_delete=models.PROTECT,
        null=False                # There should always be a default group.
    )
    date_started = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # Counter of the amount of sessions in an experiment
    # Used to obtain an incrementing ID, independent of other sessions in
    # the experiment for which this session was created.
    subject_id = models.PositiveIntegerField(null=False)

    @property
    def group_name(self):
        return self.group.name

    def complete(self):
        self.state = self.COMPLETED
        self.save()

    def delete_if_empty(self):
        # this is used in the DataPoint post_delete hook.
        # since ParticipantSession can contain multiple data points, we would
        # like to delete it only when the last associated data point is deleted
        if self.datapoint_set.count() < 1:
            self.delete()


class TargetGroup(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    name = models.CharField(
        _("experiments:models:targetgroup:name"),
        max_length=100,
        help_text=_("experiments:models:targetgroup:name:help"),
    )

    @property
    def num_started(self):
        return self.participantsession_set.count()

    @property
    def num_completed(self):
        return self.participantsession_set.filter(state=ParticipantSession.COMPLETED,
                                                  experiment_state=Experiment.OPEN).count()

    @property
    def num_pilot_completed(self):
        return self.participantsession_set.filter(state=ParticipantSession.COMPLETED,
                                                  experiment_state=Experiment.PILOTING).count()

    completion_target = models.IntegerField(
        _("experiments:models:targetgroup:completion_target"),
        help_text=_("experiments:models:targetgroup:completion_target:help"),
    )

    date_updated = models.DateTimeField(auto_now=True)

    def is_open(self):
        return self.num_completed < self.completion_target
