from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Count, Q, F, functions

from django.utils import timezone

from cdh.mail.utils import send_template_email

from experiments.models import ParticipantSession


class Command(BaseCommand):
    help = 'Sends usage statistics to admins'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, nargs='?', default=settings.LABSTAFF_EMAIL)

    def handle(self, *args, **options):
        last_sunday = timezone.now() - timedelta(days=timezone.now().weekday() + 1)
        range_from = last_sunday - timedelta(days=7)
        range_to = last_sunday

        sessions = ParticipantSession.objects.filter(
            date_updated__gte=range_from,
            date_updated__lte=range_to
        )

        per_day = sessions.annotate(day=functions.TruncDate('date_updated')).values('day').annotate(
            started=Count('id'),
            completed=Count('id', filter=Q(state=ParticipantSession.COMPLETED))
        ).values_list('day', 'started', 'completed').order_by('day')

        # Per experiment
        per_experiment = sessions.annotate(title=F('experiment__title')).values('title').annotate(
            started=Count('id'),
            completed=Count('id', filter=Q(state=ParticipantSession.COMPLETED))
        ).values_list('title', 'started', 'completed').order_by('title')

        if per_day or per_experiment:
            self.send_stats_mail(options['email'], per_day, per_experiment)
            
    def send_stats_mail(self, email, per_day, per_experiment):
        send_template_email(
            [email],
            subject="Web-experiment Stats",
            html_template="experiments/mail/stats.html",
            template_context=dict(
                per_day=per_day,
                per_experiment=per_experiment
            ),
            language='en',
        )
