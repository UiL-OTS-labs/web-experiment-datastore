from django.urls import path

from .views import ExperimentHomeView, ExperimentCreateView, \
    ExperimentEditView, ExperimentDetailView, DownloadView

app_name = 'experiments'

urlpatterns = [
    path('', ExperimentHomeView.as_view(), name='home'),
    path('new/', ExperimentCreateView.as_view(), name='new'),
    path('<int:pk>/edit/', ExperimentEditView.as_view(), name='edit'),
    path('<int:experiment>/', ExperimentDetailView.as_view(), name='detail'),
    path('<int:experiment>/download/<str:file_format>/',
         DownloadView.as_view(), name='download'),
    path('<int:experiment>/download/<int:data_point>/<str:file_format>/',
         DownloadView.as_view(), name='download_single'),
]
