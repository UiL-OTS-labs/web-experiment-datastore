from django.urls import path

from .views import AdministrationHomeView, LDAPConfigView

app_name = 'administration'

urlpatterns = [
    path('', AdministrationHomeView.as_view(), name='home'),
    path('ldap/', LDAPConfigView.as_view(), name='ldap'),
]
