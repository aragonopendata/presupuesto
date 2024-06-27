# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from budget_app.loaders import StatLoader
import os.path


class Command(BaseCommand):
    help = u"Carga las estadísticas oficiales desde fichero, _reemplazando las actuales_"

    def handle(self, *args, **options):
        # Allow overriding the data path from command line
        if len(args) < 1:
          path = os.path.join(settings.ROOT_PATH, settings.THEME, 'data') # Default: theme data folder
        else:
          path = args[0]

        StatLoader().load(path)
