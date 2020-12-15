from django.shortcuts import render
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


#
#  Error pages
#

def handler403(request, exception):
    return render(request, 'base/403.html', status=404)


def handler404(request, exception):
    return render(request, 'base/404.html', status=404)


def handler500(request, exception=None):
    return render(request, 'base/500.html', status=500)
