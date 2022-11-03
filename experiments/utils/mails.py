from django.conf import settings
from django.urls import reverse

from experiments.models import Experiment
from main.models import User
from cdh.core.mail import send_template_email


def send_new_experiment_mail(experiment: Experiment, user: User, request) -> \
        None:
    """Sent a mail to the lab staff asking them to approve the experiment. In
    addition, sent an email to the users confirming the creation of the
    experiment.
    """
    send_template_email(
        [settings.LABSTAFF_EMAIL],
        subject="New experiment",
        html_template="experiments/mail/new_experiment_staff.html",
        template_context={
            "experiment": experiment,
            "user": user,
            # By default, reverse provides a relative URL. We need an
            # absolute url
            "link": request.build_absolute_uri(reverse('administration:home'))
        },
        language='en',
    )

    recipient_list = [user.email for user in experiment.users.all()]
    send_template_email(
        recipient_list,
        subject="Confirmation new experiment",
        html_template="experiments/mail/new_experiment_user.html",
        template_context={
            "experiment": experiment,
            "user": user,
            # By default, reverse provides a relative URL. We need an
            # absolute url
            "link": request.build_absolute_uri(
                reverse('experiments:detail', args=[experiment.pk])
            )
        },
        language='en',
        from_email=settings.LABSTAFF_EMAIL,
    )
