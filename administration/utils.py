from django.conf import settings
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

    for experiment in Experiment.objects.all():
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
