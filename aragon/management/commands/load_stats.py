# -*- coding: UTF-8 -*-
from django.core.management.base import NoArgsCommand
from aragon.loaders import StatLoader
import os.path


class Command(NoArgsCommand):
    help = u"Carga las estadísticas oficiales desde fichero, _reemplazando las actuales_"

    def handle_noargs(self, **options):
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
        StatLoader().load(path)
