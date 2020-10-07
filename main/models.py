from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    def __str__(self):
        return "{} ({})".format(
            self.get_full_name(),
            self.username
        )

    def __audit_repr__(self):
        return "<{}: {}>".format(self.username, self.get_full_name())
