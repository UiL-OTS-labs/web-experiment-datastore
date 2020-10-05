from django.urls import reverse_lazy as reverse
from django.views import generic


class RedirectHomeView(generic.RedirectView):
    url = reverse('experiments:home')
