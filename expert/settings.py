"""
Django settings for expert project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from urllib.parse import urlparse

# TEST UPGRADE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expert.settings.production')
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
try:
    with open(os.path.join(os.getenv('HOME'), 'config'), 'r') as config:
        url = urlparse(config.readline())
        SECRET_KEY = config.readline()
except (IOError, TypeError):
    SECRET_KEY = "sadsfz#$#@_231dsfs&#$^123_1"
    url = False

DEBUG = False # bool(os.environ.get('DJANGO_DEBUG', False))
ALLOWED_HOSTS = ['iexpert.herokuapp.com', '127.0.0.1', 'iexpert.team', 'www.iexpert.team', 'expert-olymp.ru',
                 'www.expert-olymp.ru']

# Application definition

INSTALLED_APPS = [
    'expert.apps.MyAdminConfig',  # replaces 'django.contrib.admin'
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'userexpert',
    'info',
    'import_export',
    'app',
    'score',
    'result',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'expert.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'expert/templates')],
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

WSGI_APPLICATION = 'expert.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if url != False:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'expert',
            'USER': 'evgen',  # 'marcon1',
            'PASSWORD': '36BxXp936BxXp9',
            'HOST': 'localhost',
        }
    }
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru-en'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


STATIC_ROOT = "static/"
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "expert", "static"), )
AUTH_USER_MODEL = 'userexpert.Expert'
LOGIN_REDIRECT_URL = '/'
