from django.http import HttpResponse
from django.views import generic
import braces.views as braces

from administration.utils import generate_ldap_config
from experiments.models import Experiment


class AdministrationHomeView(braces.StaffuserRequiredMixin, generic.ListView):
    template_name = 'administration/overview.html'
    model = Experiment


class LDAPConfigView(braces.StaffuserRequiredMixin, generic.View):
    template_name = 'administration/ldap.html'

    def get(self, request, **kwargs):
        response = HttpResponse(
            generate_ldap_config(),
            content_type="text/plain",
        )

        filename = "webdav-experiment-shares.conf"
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            filename)

        return response
