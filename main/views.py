import os
from django.shortcuts import render
from django.urls import reverse_lazy as reverse
from django.views import generic
from django.conf import settings

from rest_framework.views import APIView, Response

from cdh.files.storage import CDHFileStorage


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




class StatusView(APIView):
    """status view for monitoring app"""

    def get(self, *args, **kwargs):
        status = dict(ready=False)

        # check if file storage is online
        files_path = CDHFileStorage().base_location
        if os.path.exists(files_path):
            status = dict(ready=True)

        return Response(status)
