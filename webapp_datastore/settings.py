"""
Django settings for webapp_datastore project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w784s74h5a_&0m%v=ucl#5p&w#w8qwdd@)g(s)3#ag66f5!aw0'

FIELD_ENCRYPTION_KEY = 'IhWBKI5MORNNtI5WWqZwOflEwojBACtuz9lKXwcF4HI='


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ENABLE_DEBUG_TOOLBAR = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig',

    # Django extensions
    'django_extensions',

    # django-simple-menu
    'menu',

    'experiments',
    'uil.core',

    # This has to be last, otherwise it's login/logout pages will take over
    'django.contrib.admin',
]

AUTH_USER_MODEL = 'main.User'

#AUTHENTICATION_BACKENDS = ['api.auth.backend.ApiAuthenticationBackend']

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = reverse_lazy('main:login')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',
]

if DEBUG and ENABLE_DEBUG_TOOLBAR:
    # Only enable the debug toolbar if we are in debug mode and have the
    # toolbar enabled
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware', )


ROOT_URLCONF = 'webapp_datastore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': []
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'webapp_datastore.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME':  os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'nl'
LANGUAGES = (
    ('nl', _('lang:nl')),
    ('en', _('lang:en')),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'


# Security
# https://docs.djangoproject.com/en/2.0/topics/security/

X_FRAME_OPTIONS = 'DENY'
# Local development server doesn't support https
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG

# Django CSP
# http://django-csp.readthedocs.io/en/latest/index.html
CSP_REPORT_ONLY = False
CSP_UPGRADE_INSECURE_REQUESTS = not DEBUG
CSP_INCLUDE_NONCE_IN = ['script-src']

CSP_DEFAULT_SRC = ["'self'", ]
CSP_SCRIPT_SRC = ["'self'", ]
CSP_FONT_SRC = ["'self'", 'data:', ]
CSP_STYLE_SRC = ["'self'", "'unsafe-inline'"]
CSP_IMG_SRC = ["'self'", 'data:', ]

# Django Simple Menu
# https://django-simple-menu.readthedocs.io/en/latest/index.html

MENU_SELECT_PARENTS = True
MENU_HIDE_EMPTY = False

