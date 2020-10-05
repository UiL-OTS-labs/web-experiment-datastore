from django.views import generic
import braces.views as braces

from administration.utils import generate_ldap_config
from experiments.models import Experiment


class AdministrationHomeView(braces.StaffuserRequiredMixin, generic.ListView):
    template_name = 'administration/overview.html'
    model = Experiment


class LDAPConfigView(braces.StaffuserRequiredMixin, generic.TemplateView):
    template_name = 'administration/ldap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['content'] = generate_ldap_config()

        return context