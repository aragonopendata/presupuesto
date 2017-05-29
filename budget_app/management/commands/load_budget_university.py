# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from budget_app.loaders import *
from budget_app.models import Entity
from optparse import make_option
import os.path
from django.contrib.messages.storage.base import LEVEL_TAGS


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
      make_option('--status',
        action='store',
        dest='status',
        help='Set budget status'),
    )

    help = u"Carga el presupuesto del año"

    def handle(self, *args, **options):
        source = 'U'
        if len(args) < 1:
            print "Por favor indique el año del presupuesto de la universidad a cargar."
            return
        
        year = args[0]
        status = options['status'] if options['status'] else ''
        
        print "Cargando el presupuesto de la universidad del año " ,year

        level = settings.UNIVERSITY_ENTITY_LEVEL if len(args)<2 else args[1]
        name = settings.UNIVERSITY_ENTITY_NAME if len(args)<3 else args[2]
        entity = self._get_entity(level, name)

        path = os.path.join(settings.ROOT_PATH, settings.THEME, 'data', level, year)

        # Import the loader dynamically. See http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
        module = __import__(settings.THEME+'.loaders', globals(), locals(), [settings.BUDGET_LOADER])
        loader = module.__dict__[settings.BUDGET_LOADER]()
        loader.load_university(entity, year, path, source)

    def _get_entity(self, level, name):
        entity = Entity.objects.filter(level=level, name=name)
        if not entity:
            raise Exception("Entity (%s/%s) not found" % (level, name))
        return entity[0]
