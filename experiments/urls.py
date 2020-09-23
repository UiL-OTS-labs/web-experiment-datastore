from django.urls import path

from .views import ExperimentHomeView, ExperimentCreateView, ExperimentDetailView

app_name = 'experiments'

urlpatterns = [
    path('', ExperimentHomeView.as_view(), name='home'),
    path('new/', ExperimentCreateView.as_view(), name='new'),
    path('<int:experiment>/', ExperimentDetailView.as_view(), name='detail'),
]
