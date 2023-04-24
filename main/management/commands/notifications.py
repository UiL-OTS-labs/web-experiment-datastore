from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone

from cdh.core.mail import send_template_email

from experiments.models import ParticipantSession


class Command(BaseCommand):
    help = 'Sends usage statistics to admins'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        last_sunday = timezone.now() - timedelta(days=timezone.now().weekday() + 1)
        range_from = last_sunday - timedelta(days=7)
        range_to = last_sunday

        new_sessions = ParticipantSession.objects.filter(
            date_updated__gte=range_from,
            date_updated__lte=range_to
        )

        per_day = new_sessions.annotate(
            day=models.functions.TruncDate('date_updated')
        ).values(
            'day'
        ).annotate(
            count=models.Count('day')
        ).values_list('day', 'count').order_by('day')

        per_experiment = new_sessions.annotate(
            title=models.F('experiment__title')
        ).values(
            'title'
        ).annotate(
            count=models.Count('title')
        ).values_list('title', 'count').order_by('title')

        if per_day or per_experiment:
            self.send_stats_mail(options['email'], per_day, per_experiment)

    def send_stats_mail(self, email, per_day, per_experiment):
        send_template_email(
            [email],
            subject="Web-experiment Stats",
            html_template="experiments/mail/stats.html",
            plain_template="experiments/mail/stats.txt",
            template_context=dict(
                per_day=per_day,
                per_experiment=per_experiment
            ),
            language='en',
        )
