# -*- coding: UTF-8 -*-
from django.core.management.base import NoArgsCommand
from aragon.loaders import EntityLoader
import os.path


class Command(NoArgsCommand):
    help = u"Carga la lista de entidades públicas, _reemplazando el actual_"

    def handle_noargs(self, **options):
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
        EntityLoader().load(os.path.join(path, 'entidades.csv'))
