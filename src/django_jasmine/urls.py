import os
import django

if django.VERSION >= (1, 5):
    from django.conf.urls import patterns, url
else:
    from django.conf.urls.defaults import *
from django.conf import settings

from .views import run_tests

static_root = os.path.join(os.path.dirname(__file__), 'static')


urlpatterns = patterns('django.views',
    url(r'^tests/(?P<path>.*)$', 'static.serve', {
        'document_root': os.path.join(settings.JASMINE_TEST_DIRECTORY, "spec"),
    }, name='jasmine_test'),
    url(r'^src/(?P<path>.*)$', 'static.serve', {
        'document_root': os.path.join(settings.JASMINE_TEST_DIRECTORY, "src"),
    }, name='jasmine_src'),
    url(r'^fixtures/(?P<path>.*)$', 'static.serve', {
        'document_root': os.path.join(
            settings.JASMINE_TEST_DIRECTORY, "fixtures",
        ),
    }, name='jasmine_fixtures'),
    url('^(?P<path>.*)$', run_tests, name='jasmine_test_overview'),
)
