from django.urls import path

from .views import UploadView, StatusView

app_name = 'api'

urlpatterns = [
    path('<str:access_key>/upload/', UploadView.as_view(), name='upload'),
    path('<str:access_key>/status/', StatusView.as_view(), name='status'),
    path('<str:access_key>/status/<str:field>/', StatusView.as_view(), name='status_field'),
]
