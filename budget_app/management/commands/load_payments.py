# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from budget_app.loaders import *
import os.path
import sys


class Command(BaseCommand):
    help = u"Carga los pagos correspondientes al presupuesto del año"

    def handle(self, *args, **options):
        if len(args) < 1:
            print "Por favor indique el año del presupuesto a cargar."
            return

        year = args[0]
        region_type = settings.MAIN_ENTITY_LEVEL if len(args)<2 else args[1]
        region_name = settings.MAIN_ENTITY_NAME if len(args)<3 else args[2]
        path = os.path.join(settings.ROOT_PATH, settings.THEME, 'data', region_type, year)

        # Import the loader dynamically. See http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
        module = __import__(settings.THEME+'.loaders', globals(), locals(), [settings.PAYMENTS_LOADER])
        loader = module.__dict__[settings.PAYMENTS_LOADER]()
        loader.load(region_type, region_name, year, path)
