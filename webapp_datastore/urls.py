"""webapp_datastore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from main import views

handler400 = views.handler500  # While 500 != 400, we just act like it is.
# This way the misbehaving user is treated nicely by shifting the blame to us
# (And I'm lazy)
handler403 = views.handler403
handler404 = views.handler404
handler500 = views.handler500

urlpatterns = [
    path('', include('main.urls')),
    path('administration/', include('administration.urls')),
    path('api/', include('api.urls')),
    path('experiments/', include('experiments.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('uilcore/', include('cdh.core.urls')),
    path('vue/', include('cdh.vue.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
