from django.db import models
import uuid

from uil.core.fields import EncryptedTextField

from main.models import User


class Experiment(models.Model):

    # As using UUID's as PK has some annoying implications, we just add it as
    # a separate field.
    access_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False
    )

    users = models.ManyToManyField(User)

    title = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)


class DataPoint(models.Model):

    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)

    data = EncryptedTextField()

    date_added = models.DateTimeField(auto_now_add=True)