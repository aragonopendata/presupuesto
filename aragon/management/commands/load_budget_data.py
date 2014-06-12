# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from aragon.loaders import SimplifiedBudgetLoader
import os.path
import sys


class Command(BaseCommand):
    help = u"Carga los presupuestos del nivel dado, para todos los años, reemplazando los existentes"

    def handle(self, *args, **options):
        if len(args) < 1:
            print "Por favor indique el tipo de entidad a cargar."
            return

        level = args[0]
        period = args[1]
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', level, period)

        SimplifiedBudgetLoader().load(level, path)
