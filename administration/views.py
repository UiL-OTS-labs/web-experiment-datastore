from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils.translation import ugettext_lazy as _
import braces.views as braces

from administration.utils import approve_experiment, generate_ldap_config
from auditlog.enums import Event, UserType
from auditlog.utils.log import log
from experiments.mixins import ExperimentMixin
from experiments.models import Experiment
from uil.core.views.mixins import RedirectSuccessMessageMixin


class AdministrationHomeView(braces.StaffuserRequiredMixin, generic.ListView):
    """Home view, containing a list of all experiments"""
    template_name = 'administration/overview.html'
    model = Experiment
    ordering = "-date_created"

class ApproveView(braces.StaffuserRequiredMixin, generic.DetailView):
    """View that approves experiments.

    We abuse the DetailView for it's get_object method. The template contains
    a form that posts empty data to the current page, which fires the post
    method.

    The default get method from DetailView is used to render the template.
    """
    template_name = 'administration/approve.html'
    model = Experiment

    def post(self, request, *args, **kwargs):
        experiment = self.get_object()
        approve_experiment(experiment, self.request)

        # Register action in auditlog
        log(
            Event.MODIFY_DATA,
            "Approved experiment {} ({})".format(experiment.title,
                                                 experiment.pk),
            self.request.user,
            UserType.ADMIN,
        )

        return HttpResponseRedirect(reverse('administration:home'))


class SwitchLDAPInclusionView(braces.StaffuserRequiredMixin,
                              ExperimentMixin,
                              RedirectSuccessMessageMixin,
                              generic.RedirectView):
    """This view switches the show_in_ldap_config bool of the given experiment.

    It always redirects back to the administration home view.
    """
    success_message = _('administration:messages:switched_ldap_inclusion')

    def get(self, *args, **kwargs):
        self.experiment.show_in_ldap_config = not self.experiment.show_in_ldap_config
        self.experiment.save()

        # Register action in auditlog
        log(
            Event.MODIFY_DATA,
            "Switched ldap inclusion for experiment {} ({})".format(
                self.experiment.title,
                self.experiment.pk
            ),
            self.request.user,
            UserType.ADMIN,
        )

        return super().get(*args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('administration:home')


class LDAPConfigView(braces.StaffuserRequiredMixin, generic.View):
    """This view generates a downloadable Apache config for LDAP
    authorization on the hosting server.
    """
    template_name = 'administration/ldap.html'

    def get(self, request, **kwargs):
        # Create a HttpResponse with the config as content
        response = HttpResponse(
            generate_ldap_config(),
            content_type="text/plain",
        )

        # Set the content-disposition header, so the browser sees it as a
        # downloadable file.
        filename = "webdav-experiment-shares.conf"
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            filename)

        return response
