from django.urls import path

from .views import ExperimentHomeView, ExperimentCreateView

app_name = 'experiments'

urlpatterns = [
    path('', ExperimentHomeView.as_view(), name='home'),
    path('new/', ExperimentCreateView.as_view(), name='new'),
]
