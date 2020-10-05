from django.conf import settings
from experiments.models import Experiment


def generate_ldap_config() -> str:
    config = ""

    for experiment in Experiment.objects.all():
        config += "<DocumentRoot {}{}/>\n".format(
            settings.WEBEXPERIMENT_WEBROOT,
            experiment.folder_name
        )
        config += "\trequire ldap-user"
        for user in experiment.users.all():
            config += " {}".format(user.username)

        config += "\n</DocumentRoot>\n\n"

    return config