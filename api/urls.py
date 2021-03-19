from django.urls import path

from .views import UploadView, MetadataView

app_name = 'api'

urlpatterns = [
    path('<str:access_key>/upload/', UploadView.as_view(), name='upload'),
    path('<str:access_key>/metadata/', MetadataView.as_view(), name='metadata'),
    path('<str:access_key>/metadata/<str:field>/', MetadataView.as_view(), name='metadata_field'),
]
