from django.conf import settings
from django.urls import reverse

from cdh.core.mail import send_template_email

from experiments.models import Experiment

TEMPLATE = """
# {name}
Alias /{folder} {web_root}{folder}
<Directory {web_root}{folder}>
  Options +Indexes -FollowSymLinks -MultiViews
  AllowOverride None
</Directory>
<Location /{folder}>
  DirectoryIndex disabled
  DAV on
  AuthType Basic
  Authname "gw-c-lab-web-experiments WebDav Server"
  AuthBasicProvider ldap
  AuthLDAPInitialBindAsUser on
  AuthLDAPCompareAsUser on
  AuthLDAPURL ldaps://soliscom.uu.nl/DC=soliscom,DC=uu,DC=nl?sAMAccountName?sub?(objectclass=*)
  <RequireAny>
    {permission_string}
  </RequireAny>
</Location>
"""


def generate_ldap_config() -> str:
    """This method generates the contents of the LDAP authorization config for
    the hosting server, using TEMPLATE
    """
    config = ""

    for experiment in Experiment.objects.filter(show_in_ldap_config=True):
        # Join all solis-id's together using a space
        user_string = " ".join(
            [user.username for user in experiment.users.all()]
        )
        # Prepend the LDAP directive
        permission_string = "Require ldap-user {}".format(user_string)

        # Format the template for this experiment
        config += TEMPLATE.format(
            name=experiment.title,
            folder=experiment.folder_name,
            permission_string=permission_string,
            web_root=settings.WEBEXPERIMENT_WEBROOT,
        )

    return config


def approve_experiment(experiment: Experiment, request) -> None:
    """Approves an experiment, and informs users of the approval

    :param experiment: :class:`Experiment` the experiment to approve
    :param request: Django request. Used to create an absolute URL in the mail
    """
    experiment.approved = True
    experiment.save()

    sent_confirmation_email(experiment, request)


def sent_confirmation_email(experiment: Experiment, request) -> None:
    """Sends the confirmation email

    :param experiment: :class:`Experiment` that was apprvoed
    :param request: Django request. Used to create an absolute URL in the mail
    """
    recipient_list = [user.email for user in experiment.users.all()]

    # Add lab-staff as well, so the others know this experiment has been
    # approved.
    recipient_list.append(settings.LABSTAFF_EMAIL)

    send_template_email(
        recipient_list,
        subject="Your experiment has been approved",
        html_template="administration/mail/experiment_approved.html",
        template_context={
            "experiment": experiment,
            # By default, reverse generates a relative url. Using
            # build_absolute_url gives us an absolute url that actually works
            # in mails.
            "link": request.build_absolute_uri(
                reverse('experiments:detail', args=[experiment.pk])
            ),
        },
        from_email=settings.LABSTAFF_EMAIL,
        language='en',
    )
