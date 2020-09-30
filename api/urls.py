from django.urls import path

from .views import UploadView

app_name = 'api'

urlpatterns = [
    path('<str:access_key>/upload/', UploadView.as_view(), name='upload'),
]
