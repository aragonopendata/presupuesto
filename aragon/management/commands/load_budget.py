# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from aragon.loaders import BudgetLoader
import os.path
import sys


class Command(BaseCommand):
    help = u"Carga el presupuesto del año"

    def handle(self, *args, **options):
        if len(args) < 1:
            print "Por favor indique el año del presupuesto a cargar."
            return

        year = args[0]
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'comunidad', year)

        BudgetLoader().load('comunidad', 'Aragón', year, path)
