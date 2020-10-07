from django.urls import path

from .views import AdministrationHomeView, LDAPConfigView, ApproveView, SwitchLDAPInclusionView

app_name = 'administration'

urlpatterns = [
    path('', AdministrationHomeView.as_view(), name='home'),
    path('<int:pk>/approve/', ApproveView.as_view(), name='approve'),
    path('<int:experiment>/switch_ldap_inclusion/',
         SwitchLDAPInclusionView.as_view(), name='switch_ldap_inclusion'),
    path('ldap/', LDAPConfigView.as_view(), name='ldap'),
]
