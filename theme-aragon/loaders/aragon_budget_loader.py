# -*- coding: UTF-8 -*-

from budget_app.models import *
from budget_app.loaders.budget_loader import BudgetLoader
import csv
import os.path


class AragonBudgetLoader(BudgetLoader):
    # The client doesn't like the Areas defined in the budget (which are, to be honest,
    # quite useless and ugly-sounding), so they've requested - and I've conceded - that
    # the policies are grouped in four areas defined by themselves. It's easier to do it
    # when loading the data, instead of modifying the original budget files, harder to track.
    def _map_policy_to_new_area(self, policy):
        map = {
          '0': ['01'],
          '1': ['11','12','14','46','55','63','91'],
          '2': ['13','31','32','41','42','43','44','45'],
          '3': ['51','53','54','61','62','64','71','72','73','75'],
        }

        for area, policies in map.iteritems():
            if policy in policies:
                return area
        return ""

    def get_default_functional_categories(self):
        categories = BudgetLoader.get_default_functional_categories(self)

        # Create custom areas (I could put this in a file, but doesn't feel worth it)
        categories.append({ 'area':'0', 'description': 'Deuda'})
        categories.append({ 'area':'1', 'description': 'Administración'})
        categories.append({ 'area':'2', 'description': 'Bienestar Social'})
        categories.append({ 'area':'3', 'description': 'Desarrollo Económico'})

        return categories

    def add_functional_category(self, items, line):
        # Read the description. There are patches to the budget descriptions that are
        # more easily done here (although it's ugly to have these hardcoded things around).
        description = line[6]
        if description == 'Salud Pública':
            description = 'Prevención de la Salud'
        description = self._escape_unicode(description)

        # We map the original policy into the four custom-made areas, as explained above.
        # We prepend all the children categories with the new area value so the visualizations
        # later know which area a policy or programme belongs to, as that's used to pick colors.
        policy = line[2]
        new_area = self._map_policy_to_new_area(policy)

        items.append({
                'area': new_area,
                'policy': new_area + policy,
                'function': (new_area + line[3] if line[3] != "" else None),
                'programme': (new_area + line[4] if line[4] != "" else None),
                'description': description.title()
            })

    def add_economic_category(self, items, line):
        # Read the description. There are patches to the budget descriptions that are
        # more easily done here (although it's ugly to have these hardcoded things around).
        description = line[7]
        if description == 'Del Exterior':
            description = 'Fondos Europeos'
        description = self._escape_unicode(description)

        items.append({
                'expense': (line[1].upper() == 'G'),
                'chapter': (line[2] if line[2] != "" else None),
                'article': (line[3] if line[3] != "" else None),
                'heading': (line[4] if line[4] != "" else None),
                'subheading': (line[5] if line[5] != "" else None),
                'description': description
            })

    def add_data_item(self, items, line, is_expense, is_actual):
        # Get the amount. For execution data, pick "Obligaciones/Créditos reconocidas/os"
        if is_actual:
            if (is_expense and len(line) < 11) or (not is_expense and len(line) < 10):
                print "ALERTA: Faltan campos en la línea: %s" % line
                return
            else:
                amount = line[10 if is_expense else 9]

        else:
            amount = line[6]

        # See explanation above about the remapping of areas into four 'super-areas'
        if is_expense:
            fc_code = '0' + line[2] if len(line[2]) < 4 else line[2]    # Inconsistent 2012-2013
            fc_area = self._map_policy_to_new_area(fc_code[0:2])
            fc_policy = fc_area + fc_code[0:2]
            fc_function = fc_area + fc_code[0:3]
            fc_programme = fc_area + fc_code
        else:
            fc_area = 'X'
            fc_policy = 'XX'
            fc_function = 'XXX'
            fc_programme = 'XXXX'

        # Gather all the relevant bits and store them to be processed
        items.append({
                'ic_code': '0' + line[1] if len(line[1]) < 5 else line[1], # Inconsistent 2012-2013
                'fc_area': fc_area,
                'fc_policy': fc_policy,
                'fc_function': fc_function,
                'fc_programme': fc_programme,
                'ec_chapter': line[3][0],
                'ec_article': (line[3][0:2] if len(line[3])>=2 else None),
                'ec_heading': (line[3][0:3] if len(line[3])>=3 else None),
                'ec_subheading': (line[3] if len(line[3])>=4 else None),
                'ec_code': line[3], # Redundant, but convenient
                'fdc_code': line[4],
                'item_number': '',
                'description': self._escape_unicode(line[5]),
                'amount': self._read_spanish_number(amount)
            })

    def _escape_unicode(self, s):
        return unicode(s, encoding='unicode-escape')
