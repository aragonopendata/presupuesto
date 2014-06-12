# -*- coding: UTF-8 -*-
from django.core.management.base import NoArgsCommand
from aragon.loaders import GlossaryLoader
import os.path


class Command(NoArgsCommand):
    help = u"Carga los términos del glosario desde un fichero, _reemplazando el actual_"

    def handle_noargs(self, **options):
        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
        GlossaryLoader().load(os.path.join(path, 'glosario.csv'))
