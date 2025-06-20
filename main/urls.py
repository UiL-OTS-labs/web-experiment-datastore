from django.urls import path
from django.contrib.auth import views as auth_views

from main.views import RedirectHomeView, HelpPageView, StatusView

app_name = 'main'

urlpatterns = [
    path('', RedirectHomeView.as_view(), name='home'),
    path('help/', HelpPageView.as_view(), name='help'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('status/', StatusView.as_view(), name='status'),
]
