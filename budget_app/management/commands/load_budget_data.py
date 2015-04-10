# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.conf import settings
from budget_app.loaders import AragonBulkBudgetLoader
import os.path
import sys


class Command(BaseCommand):
    help = u"Carga los presupuestos del nivel dado, para el periodo indicado, reemplazando los existentes"

    def handle(self, *args, **options):
        if len(args) < 2:
            print "Por favor indique el tipo de entidad y el periodo a cargar."
            return

        level = args[0]
        period = args[1]
        path = os.path.join(settings.ROOT_PATH, settings.THEME, 'data', level, period)

        AragonBulkBudgetLoader().load(level, path)
