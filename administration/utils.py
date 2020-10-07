from django.conf import settings
from uil.core.utils.mail import send_template_email

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
  AuthLDAPURL "ldaps://ldap.hum.uu.nl/dc=uu,dc=nl?uid?sub"
  <RequireAny>
    {permission_string}
  </RequireAny>
</Location>
"""


def generate_ldap_config() -> str:
    config = ""

    for experiment in Experiment.objects.filter(show_in_ldap_config=True):
        user_string = " ".join(
            [user.username for user in experiment.users.all()]
        )
        permission_string = "Require ldap-user {}".format(user_string)

        config += TEMPLATE.format(
            name=experiment.title,
            folder=experiment.folder_name,
            permission_string=permission_string,
            web_root=settings.WEBEXPERIMENT_WEBROOT,
        )

    return config


def approve_experiment(experiment: Experiment) -> None:
    experiment.approved = True
    experiment.save()

    sent_confirmation_email(experiment)


def sent_confirmation_email(experiment: Experiment) -> None:
    recipient_list = [user.email for user in experiment.users.all()]

    # Add lab-staff as well, so the others know this experiment has been
    # approved.
    recipient_list.append(settings.LABSTAFF_EMAIL)

    send_template_email(
        recipient_list,
        "Your experiment has been approved",
        "administration/mail/experiment_approved",
        {
            "experiment": experiment,
        },
        from_email=settings.LABSTAFF_EMAIL,
        language='en',
    )
