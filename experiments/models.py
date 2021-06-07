from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

from uil.core.fields import EncryptedTextField

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
            RegexValidator(r"[a-zA-Z0-9\-_]*")
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


class DataPoint(models.Model):
    """Model to hold data from a participant in an experiment"""
    class Meta:
        unique_together = ['experiment', 'number']

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    # Counter of the amount of DP's in an experiment
    # Used to display an incrementing ID, independent from other experiments
    number = models.PositiveIntegerField(null=False)

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
