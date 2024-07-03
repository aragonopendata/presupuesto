# -*- coding: UTF-8 -*-

import os.path
import sys
SETTINGS_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(SETTINGS_PATH, '..')

import os
from dotenv import load_dotenv

load_dotenv()


# ENVIRONMENT-SPECIFIC SETTINGS
#
# Load a non-versioned-controlled local file if it exists.
#
# Note: I thought initially I'd insert it at the very end, so it could override any setting,
# but it turns out it's more useful to load it at the beginning, so I can set the database credentials.
# I could potentially split it in two (like Rails does), but feels overkill
#
# try:
#     execfile(os.path.join(ROOT_PATH, 'local_settings.py'), globals(), locals())
# except IOError:
#     pass


# THEME-SPECIFIC SETTINGS
# Note: After looking into ways of importing modules dynamically, I decided this was the simplest solution
# Following http://igorsobreira.com/2010/09/12/customize-settingspy-locally-in-django.html
#
# Pick a theme by setting the THEME variable in 'local_settings.py'.
#
# if ENV.get('THEME'):
#     THEME=ENV.get('THEME')
#     execfile( os.path.join(ROOT_PATH, THEME, 'settings.py'), globals(), locals())
# else:
#    print "Please set the environment variable THEME in your local_settings.py file."
#    sys.exit(1)
THEME = os.getenv('THEME', 'theme-aragon')
if THEME == 'theme-aragon':
    execfile(os.path.join(ROOT_PATH, THEME, 'settings.py'), globals(), locals())


# DJANGO SETTINGS
#
# DEBUG = ENV.get('DEBUG', False)
# TEMPLATE_DEBUG = ENV.get('TEMPLATE_DEBUG', DEBUG)
DEBUG = os.getenv('DEBUG', False)
TEMPLATE_DEBUG = os.getenv('TEMPLATE_DEBUG', DEBUG)



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DATABASE_NAME', 'presupuesto'),
        'USER': os.getenv('DATABASE_USER', 'presupuesto'),                   # Not used with sqlite3.
        'PASSWORD':os.getenv('DATABASE_PASSWORD', 'presupuesto'),           # Not used with sqlite3.
        'HOST': os.getenv('DATABASE_HOST', 'postgres'), # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                 # Set to empty string for default. Not used with sqlite3.
    }
}

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Madrid'

# Location of translation files (used by themes to override certain strings)
LOCALE_PATHS = (
    os.path.join(os.path.dirname(__file__), '..', THEME, 'locale'),
)

# Ensure LANGUAGES is defined for LocaleMiddleware. Multilingual themes
# will have defined this beforehand with their particular language list.
if not 'LANGUAGES' in locals():
    # All choices can be found here: http://www.i18nguy.com/unicode/language-identifiers.html
    LANGUAGES = (
      ('es-ES', 'Castellano'),
    )

# Base language code for this installation. Selects the first from the list of available ones.
# See https://docs.djangoproject.com/en/1.4//topics/i18n/translation/#how-django-discovers-language-preference
LANGUAGE_CODE = locals()['LANGUAGES'][0][0]


SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(ROOT_PATH, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_PATH, THEME, 'static'),
    os.path.join(ROOT_PATH, 'budget_app', 'static')
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder', # add Django Compressor's file finder
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')e2qrwa6e$u30r0)w=52!0j1_&amp;$t+y3z!o-(7ej0=#i!c7pjuy'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

if DEBUG:
    MIDDLEWARE_CLASSES = (
        'django_user_agents.middleware.UserAgentMiddleware',
        'project.middleware.SmartUpdateCacheMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware', #
        'django.middleware.csrf.CsrfViewMiddleware', #
#        'django.middleware.locale.LocaleMiddleware', #
	'django.middleware.cache.FetchFromCacheMiddleware'
    )
else:
    MIDDLEWARE_CLASSES = (
        'django_user_agents.middleware.UserAgentMiddleware',
        'project.middleware.SmartUpdateCacheMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware', #
        'django.middleware.csrf.CsrfViewMiddleware', #
#        'django.middleware.locale.LocaleMiddleware', #
        # 'django.contrib.auth.middleware.AuthenticationMiddleware',
        # 'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.cache.FetchFromCacheMiddleware',
        # Uncomment the next line for simple clickjacking protection:
        # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    )

ROOT_URLCONF = 'project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'project.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '..', THEME, 'templates'),
    os.path.join(os.path.dirname(__file__), '..', 'templates')
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    # 'django.contrib.auth',
    'django_user_agents',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    #'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django_jasmine',
    'compressor',
    THEME,
    'budget_app'
)

# Uncomment next line to force JS compression in development (Debug=True)
# COMPRESS_ENABLED = True

# Configure Compressor for Jinja2
JINJA2_EXTENSIONS = [
    'compressor.contrib.jinja2ext.CompressorExtension',
]

# Needed by django_compressor. See http://django-compressor.readthedocs.org/en/latest/jinja2/#id1
def COMPRESS_JINJA2_GET_ENVIRONMENT():
    from coffin.common import env
    return env

# Setup Jasmine folder for js unit
# test https://github.com/Aquasys/django-jasmine#installation
JASMINE_TEST_DIRECTORY = (
    os.path.join(os.path.dirname(__file__), '..', 'tests')
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
      'simple': {
            'format': '%(levelname)s %(name)s %(module)s %(message)s'
      },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'budget_app': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },

    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    # "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages"
)

SEARCH_CONFIG = os.getenv('SEARCH_CONFIG', 'pg_catalog.english')


DEFAULT_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}
CACHES = os.getenv('CACHES', DEFAULT_CACHES)

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 90 * 60 * 60 * 24  # 90 Days: data doesn't actually change
CACHE_MIDDLEWARE_KEY_PREFIX = 'budget_app'

# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
USER_AGENTS_CACHE = 'default'

# if exists, load local_settings.py
try:
    from local_settings import *
except ImportError:
    pass