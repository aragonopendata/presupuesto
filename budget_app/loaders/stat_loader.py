# -*- coding: UTF-8 -*-
from budget_app.models import InflationStat, PopulationStat, Entity
import csv
import re
import os.path


class StatLoader:
    def load(self, path):
        self._delete_all()
        self.load_inflation(os.path.join(path, 'inflacion.csv'))
        self.load_population(os.path.join(path, 'poblacion.csv'))

    def load_inflation(self, filename):
        print "Cargando estadísticas oficiales de inflación de %s..." % filename
        reader = csv.reader(open(filename, 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):  # Ignore comments
                continue

            print "  Cargando inflación para el año %s..." % line[0]
            stat = InflationStat(year=line[0], inflation=line[1])
            stat.save()

    def load_population(self, filename):
        print "Cargando estadísticas oficiales de población de %s..." % filename
        reader = csv.reader(open(filename, 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):  # Ignore comments
                continue

            code = line[0]
            name = line[1]
            year = line[2]
            population = line[3]

            print "  Cargando población para %s (%s)..." % (name, year)
            entity = self._get_entity(code, name)
            stat = PopulationStat(entity=entity, year=year, population=population)
            stat.save()

    def _delete_all(self):
        InflationStat.objects.all().delete()
        PopulationStat.objects.all().delete()

    def _get_entity(self, code, name):
        entity = Entity.objects.filter(code=code)
        if not entity:
            raise Exception("Entity (%s/%s) not found" % (code, name))
        return entity[0]
