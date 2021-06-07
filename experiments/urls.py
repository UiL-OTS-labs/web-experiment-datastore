from django.urls import path

from .views import ExperimentHomeView, ExperimentCreateView, \
    ExperimentEditView, ExperimentDetailView, DownloadView, \
    DeleteExperimentView, DeleteDataPointView, DeleteAllDataView, \
    ExperimentHomeApiView

app_name = 'experiments'

urlpatterns = [
    path('', ExperimentHomeView.as_view(), name='home'),
    path('api/home/', ExperimentHomeApiView.as_view(), name='home_api'),

    path('new/', ExperimentCreateView.as_view(), name='new'),
    path('<int:pk>/edit/', ExperimentEditView.as_view(), name='edit'),

    path('<int:experiment>/', ExperimentDetailView.as_view(), name='detail'),

    path('<int:pk>/delete/', DeleteExperimentView.as_view(),
         name='delete_experiment'),

    path('<int:experiment>/data/<int:pk>/delete/',
         DeleteDataPointView.as_view(), name='delete_datapoint'),
    path('<int:experiment>/data/delete/', DeleteAllDataView.as_view(),
         name='delete_all_data'),

    path('<int:experiment>/data/<str:file_format>/',
         DownloadView.as_view(), name='download'),
    path('<int:experiment>/data/<int:data_point>/<str:file_format>/',
         DownloadView.as_view(), name='download_single'),
]
