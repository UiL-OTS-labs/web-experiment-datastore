from django.urls import reverse_lazy as reverse
from django.views import generic
from django.conf import settings


class RedirectHomeView(generic.RedirectView):
    url = reverse('experiments:home')


class HelpPageView(generic.TemplateView):
    template_name = 'main/help.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['labstaff_email'] = settings.LABSTAFF_EMAIL

        return context
