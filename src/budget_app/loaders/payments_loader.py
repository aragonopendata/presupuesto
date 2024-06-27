# -*- coding: UTF-8 -*-
from budget_app.models import *
from decimal import *
import datetime
import csv
import os
import re

# Generic payments loader
class PaymentsLoader:

    def load(self, level, name, year, path):
        items = self.parse_data(os.path.join(path, 'pagos.csv'))

        # Find the public body the payments relates to
        entity = Entity.objects.filter(level=level, name=name)
        if not entity:
            raise Exception("Entity (%s/%s) not found" % (level, name))
        else:
            entity = entity[0]

        # Find the budget the payments relates to
        budget = Budget.objects.filter(entity=entity, year=year)
        if not budget:
            raise Exception("Budget (%s/%s) not found" % (entity.name, year))
        else:
            budget = budget[0]

        # Delete previous payments for the given budget if they exist
        Payment.objects.filter(budget=budget).delete()

        # Store the data in the database
        print u"Cargando pagos para entidad '%s' año %s..." % (entity.name, year)
        self.load_items(budget, items)


    def parse_data(self, filename):
        items = []        
        if os.path.isfile(filename):
            print "Leyendo datos de %s..." % filename
            reader = csv.reader(open(filename, 'rb'))
            for index, line in enumerate(reader):
                if re.match("^#", line[0]):         # Ignore comments
                    continue

                if re.match("^ +$", line[0]):       # Ignore empty lines
                    continue

                # Finally, we have useful data
                items.append(line)

        return items


    # Parse an input line into fields
    # Note: we're ignoring some fields, not really relevant or not populated often enough to 
    # be useful: period, NIF and source filename.
    def parse_item(self, budget, line):
        # The date is not always available
        try:
            date=datetime.datetime.strptime(line[4], "%Y-%m-%d")
        except ValueError:
            date=None

        return {
            'area': line[0].strip(),
            'fc_code': line[1].strip(),
            'ec_code': line[2].strip(),
            'payee': self._titlecase(line[6].strip()),
            'contract_type': line[7].strip(),
            'date': date,
            'description': self._spanish_titlecase(line[8].strip()),
            'amount': self._get_amount(line)
        }


    # Note that the payment data may not be fully classified along the functional or economic
    # categories. When loading budget data for small entities we fill this up using dummy categories, 
    # since we have complex queries in the application that expect a number of different tables
    # to match perfectly (and they were built when the data was always fine, for historical reasons).
    # But for payments we're going to leave the fields null in the database, should be cleaner.
    def load_items(self, budget, items):
        for item in items:
            fields = self.parse_item(budget, item)

            # Ignore entries with no amount
            if fields['amount'] == 0:
                continue

            # Fetch economic category
            if fields['ec_code']!='':
                ec = EconomicCategory.objects.filter(expense=True,
                                                    chapter=fields['ec_code'][0],
                                                    article=fields['ec_code'][0:2] if len(fields['ec_code']) >= 2 else None,
                                                    heading=fields['ec_code'][0:3] if len(fields['ec_code']) >= 3 else None,
                                                    subheading = None,
                                                    budget=budget)
                if not ec:
                    print u"ALERTA: No se encuentra la categoría económica '%s' para '%s': %s€" % (fields['ec_code'], fields['description'].decode("utf8"), fields['amount']/100)
                    continue
                else:
                    ec = ec[0]
            else:
                ec = None

            # Fetch functional category
            if fields['fc_code']!='':
                fc = FunctionalCategory.objects.filter( area=fields['fc_code'][0:1],
                                                        policy=fields['fc_code'][0:2],
                                                        function=fields['fc_code'][0:3],
                                                        programme=fields['fc_code'],
                                                        budget=budget)
                if not fc:
                    print u"ALERTA: No se encuentra la categoría funcional '%s' para '%s': %s€" % (fields['fc_code'], fields['description'].decode("utf8"), fields['amount']/100)
                    continue
                else:
                    fc = fc[0]
            else:
                fc = None

            Payment(area=fields['area'],
                    functional_category = fc,
                    economic_category = ec,
                    economic_concept = fields['ec_code'],
                    date=fields['date'],
                    payee=fields['payee'],
                    contract_type=fields['contract_type'],
                    expense=True,
                    amount=fields['amount'],
                    description=fields['description'],
                    budget=budget).save()


    # Read number in English format (123,456.78), and return as number of cents
    def _read_english_number(self, s):
        if (s.strip()==""):
            return 0

        return int(Decimal(s.replace(',', ''))*100)

    # Get the amount for a budget line
    def _get_amount(self, item):
        return self._read_english_number(item[9])

    # TODO: These below are probably useful enough to move to some base/utils class
    # (It may be worth checking also what other loaders are doing regarding Unicode, since it's always
    # a tricky business.)

    # If the given string is all uppercase, convert to titlecase
    def _titlecase(self, s):
        if s.isupper():
          # We need to do the casing operation on an Unicode string so it handles accented characters correctly
          return unicode(s, encoding='utf8').title()
        else:
          return s

    # If the given string is all uppercase, convert to 'spanish titlecase', i.e. only first letter is upper
    def _spanish_titlecase(self, s):
        if s.isupper():
          # We need to do the casing operation on an Unicode string so it handles accented characters correctly
          s = unicode(s, encoding='utf8')
          return s[0].upper() + s[1:].lower()
        else:
          return s