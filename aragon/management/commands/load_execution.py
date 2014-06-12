# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from aragon.loaders import BudgetLoader
import os.path


class Command(BaseCommand):
    help = u"Carga la ejecución presupuestaria del año"

    def handle(self, *args, **options):
        if len(args) == 0:
            print "Por favor indique el año de la ejecución presupuestaria a cargar."
            return

        year = args[0]
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'comunidad', year)
        BudgetLoader().load_execution('comunidad', 'Aragón', year, path)
