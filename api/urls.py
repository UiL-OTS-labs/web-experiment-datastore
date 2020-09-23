from django.urls import path

from .views import UploadView, ShowDataView

app_name = 'api'

urlpatterns = [
    path('upload/', UploadView.as_view(), name='upload'),
    path('show/<int:pk>', ShowDataView.as_view(), name='show')
]
