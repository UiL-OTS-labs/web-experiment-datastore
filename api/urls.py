from django.urls import path

from .views import UploadView, MetadataView, ParticipantView

app_name = 'api'

urlpatterns = [
    path('<str:access_key>/upload/', UploadView.as_view(), name='upload'),
    path('<str:access_key>/metadata/', MetadataView.as_view(), name='metadata'),
    path('<str:access_key>/metadata/<str:field>/', MetadataView.as_view(), name='metadata_field'),

    path('<str:access_key>/participant/', ParticipantView.as_view(), name='participant'),
    path('<str:access_key>/upload/<str:participant_id>/', UploadView.as_view(), name='upload'),
]
