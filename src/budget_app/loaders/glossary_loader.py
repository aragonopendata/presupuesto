# -*- coding: UTF-8 -*-
from budget_app.models import GlossaryTerm
import csv
import re


class GlossaryLoader:
    def load(self, filename):
        self._delete_all()

        print "Cargando glosario de %s..." % filename
        reader = csv.reader(open(filename, 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):  # Ignore comments
                continue

            print "  Cargando término %s..." % line[0]
            term = GlossaryTerm(title=line[0], description=line[1])
            term.save()

    def _delete_all(self):
        GlossaryTerm.objects.all().delete()
