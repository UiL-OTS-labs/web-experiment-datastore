from django.db import models
from django.db.models.functions import Now

from auditlog import fields as auditlog_fields
from auditlog.enums import Event, UserType
from auditlog.utils.get_choices import get_choices_from_enum
import uil.core.fields as encrypted_models


class LogEntry(models.Model):
    """Describes an event that should be logged"""
    class Meta:
        # Only allow additions
        default_permissions = ('add',)

    # Describes the event in a code format
    event = models.TextField(
        choices=get_choices_from_enum(Event)
    )

    # Human readable description of the event, should provide some more info
    # than the event field.
    message = models.TextField(
        null=True,
        blank=True,
    )

    # The user that created the event. Stored as a string to allow for
    # more flexibility. (Using the User model would not allow system actions
    # for example).
    user = models.TextField(
        null=True,
        blank=True,
    )

    # Describes the user's role in the application
    user_type = models.TextField(
        null=True,
        blank=True,
        choices=get_choices_from_enum(UserType),
    )

    # Any additional data that provides more info about the event. Accepts
    # most Python data, as it's stored as a JSON string.
    extra = auditlog_fields.JSONField(
        null=True,
        blank=True,
    )

    # Record is the timestamp of the original entry, from Python's
    # perspective. It's encrypted to discourage tempering.
    record = encrypted_models.EncryptedDateTimeField(
        auto_now_add=True,
    )

    # DB record date is the timestamp of the original entry, from the
    # database's perspective
    db_record_date = models.DateTimeField(
        default=Now()
    )

    # Last modification if the timestamp of the last edit, from Python's
    # perspective. NOTE: this should be the same as record_date. If this
    # differs, the log was modified. (Which should NOT happen).
    last_modification = models.DateTimeField(
        auto_now=True,
    )
