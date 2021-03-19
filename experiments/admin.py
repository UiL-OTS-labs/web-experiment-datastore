from django.contrib import admin
from django.db import models
from django.forms import widgets

from .models import Experiment


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('title', 'state', 'approved', 'date_created')
    readonly_fields = ('access_id', 'date_created', )
    fieldsets = (
        ('Info', {
            'fields': ('title', 'access_id', 'date_created')
        }),
        ('Access', {
            'fields': ('users', 'approved')
        }),
        ('Experiment server', {
            'fields': ('folder_name', 'show_in_ldap_config'),
        }),
    )
    formfield_overrides = {
        models.TextField: {'widget': widgets.TextInput},
    }
