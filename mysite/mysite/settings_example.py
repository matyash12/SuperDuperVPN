"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!dg=on5^7js79xrv$f)f!=97bf*i#%ruk(*1(rs!z--#4jo7w%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost','127.0.0.1','django','nginx','10.0.0.*']


# Application definition

INSTALLED_APPS = [
    'celery',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'SuperDuperVPN.apps.SuperdupervpnConfig',
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

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

#old sqlite config
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}
#mysql config
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'superdupervpn',
        'USER': 'django',
        'PASSWORD': 'password',
        'HOST': 'db',  # Set to your MySQL host, e.g., '127.0.0.1' or 'mysql.example.com'
        'PORT': '3306',  # Default MySQL port is 3306
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Celery settings
# Celery configuration settings

# set the celery broker url
CELERY_BROKER_URL = 'redis://redis:6379/0'
  
# set the celery result backend
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
  
# set the celery timezone
CELERY_TIMEZONE = 'UTC'


#where is wireguard configuration file stored.
#+DO a backup before using this
WIREGUARD_CONF_FILE_PATH = '/wireguardconfig/wg0.conf'
WIREGUARD_COMMAND_TO_RESTART = 'systemctl restart wg-quick@wg0'

#add_peer default values for generate method
DEFAULT_ALLOWED_IPS = '0.0.0.0/0, ::/0'
DEFAULT_DNS = '8.8.8.8' #google


#place where when a wireguard config file is generated for it will be saved here. (temporelary)
CLIENT_CONFIG_FILE_FOLDER = 'SuperDuperVPN/templates/generated_files/' #end with '/'
CLIENT_CONFIG_FILE_FOLDER_QR_CODE = 'SuperDuperVPN/templates/generated_qr_codes/'#end with '/'