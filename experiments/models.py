from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext as _
import uuid

from uil.core.fields import EncryptedTextField

from main.models import User


class Experiment(models.Model):

    # As using UUID's as PK has some annoying implications, we just add it as
    # a separate field.
    access_id = models.UUIDField(
        _("experiments:models:experiment:access_id"),
        unique=True,
        default=uuid.uuid4,
        editable=False
    )

    users = models.ManyToManyField(
        User
    )

    folder_name = models.TextField(
        _("experiments:models:experiment:folder_name"),
        validators=[
            RegexValidator(r"[a-zA-Z0-9\-_]*")
        ]
    )

    title = models.TextField(
        _("experiments:models:experiment:title"),
    )

    date_created = models.DateTimeField(
        _("experiments:models:experiment:date_created"),
        auto_now_add=True
    )

    def __str__(self):
        return self.title


class DataPoint(models.Model):

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    data = EncryptedTextField(
        _("experiments:models:datapoint:data"),
    )

    date_added = models.DateTimeField(
        _("experiments:models:datapoint:date_added"),
        auto_now_add=True
    )
