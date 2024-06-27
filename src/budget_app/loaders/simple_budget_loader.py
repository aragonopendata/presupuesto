# -*- coding: UTF-8 -*-
from budget_app.models import *
from decimal import *
import csv
import os
import re

class SimpleBudgetLoader:

    def load(self, entity, year, path, status):
        # Parse the incoming data and keep in memory
        budget_items = []        
        self.parse_budget_data(budget_items, os.path.join(path, 'ingresos.csv'))
        self.parse_budget_data(budget_items, os.path.join(path, 'gastos.csv'))
        self.parse_budget_data(budget_items, os.path.join(path, 'ejecucion_ingresos.csv'))
        self.parse_budget_data(budget_items, os.path.join(path, 'ejecucion_gastos.csv'))

        # Now load the data one budget at a time
        self.load_budget(path, entity, year, status, budget_items)


    # OVERRIDE THIS!
    # I don't think it's worth offering a base implementation, not at this point at least, since
    # every input data we get has a different structure, and there's value in keeping the CSV files
    # as close as possible to the original database, PDF, XLS, whatever.
    def parse_item(self, filename, line):
        return {}


    def parse_budget_data(self, budget_items, filename):
        if os.path.isfile(filename):
            print "Leyendo datos de %s..." % filename
            reader = csv.reader(open(filename, 'rb'))
            for index, line in enumerate(reader):
                if re.match("^#", line[0]):         # Ignore comments
                    continue

                if re.match("^ +$", line[0]):       # Ignore empty lines
                    continue

                # Finally, we have useful data
                budget_items.append(self.parse_item(filename, line))


    def load_budget(self, path, entity, year, status, items):
        # Delete previous budget for the given entity/year if it exists
        Budget.objects.filter(entity=entity, year=year).delete()

        # Store the data in the database
        print u"Cargando presupuesto para entidad '%s' año %s..." % (entity.name, year)
        budget = Budget(entity=entity, year=year, status=status)
        budget.save()

        # Load the economic and functional classification from a manually edited file
        self.load_economic_classification(path, budget)
        self.load_institutional_classification(path, budget)
        self.load_functional_classification(path, budget)

        # Process the budget item
        self.load_budget_items(budget, items)


    def load_budget_items(self, budget, budget_items):
        # Since the incoming data is not fully classified along the four dimensions we defined
        # for the main budget (Aragón, the good one), we are forced to assign the items a 
        # catch-all fake category. (Leaving the category blank would be another possibility,
        # but we'd have to modify the DB structure for that, and also our breakdown queries,
        # so I'm going this slightly hackier way first.)
        dummy_fdc = FundingCategory(expense=True,   # True/False doesn't really matter
                                    source='X',
                                    fund_class=None,
                                    fund=None,
                                    description='Desconocido',
                                    budget=budget)
        dummy_fdc.save()

        # Income data is often not classified functionally, but we need every budget item to be classified
        # along all dimensions (at least for now), because of the way we denormalize/join the data in the app.
        # So we create a fake functional category that will contain all the income data.
        dummy_fc = FunctionalCategory(  area='X',
                                        policy='XX',
                                        function='XXX',
                                        programme='XXXX',
                                        description='Ingresos',
                                        budget=budget)
        dummy_fc.save()


        # Store data in the database
        budgeted_income = 0
        budgeted_expense = 0
        for item in budget_items:
            if item['amount'] == 0:
                continue

            # Check whether budget income and expense match
            if not item['is_actual']:
                if item['is_expense']:
                    budgeted_expense += item['amount']
                else:
                    budgeted_income += item['amount']

            # Fetch economic category
            ec = EconomicCategory.objects.filter(expense=item['is_expense'],
                                                chapter=item['ec_code'][0],
                                                article=item['ec_code'][0:2] if len(item['ec_code']) >= 2 else None,
                                                heading=item['ec_code'][0:3] if len(item['ec_code']) >= 3 else None,
                                                subheading = None,
                                                budget=budget)
            if not ec:
                print u"ALERTA: No se encuentra la categoría económica '%s' para '%s': %s€" % (item['ec_code'].decode("utf8"), item['description'].decode("utf8"), item['amount']/100)
                continue
            else:
                ec = ec[0]

            # Fetch economic category
            ic = InstitutionalCategory.objects.filter(  institution=item['ic_code'][0],
                                                        section=item['ic_code'][0:2] if len(item['ic_code']) >= 2 else None,
                                                        department=item['ic_code'] if len(item['ic_code']) >= 3 else None,
                                                        budget=budget)
            if not ic:
                print u"ALERTA: No se encuentra la categoría institucional '%s' para '%s': %s€" % (item['ic_code'].decode("utf8"), item['description'].decode("utf8"), item['amount']/100)
                continue
            else:
                ic = ic[0]

            # Fetch functional category, only for expense items
            if item['is_expense']:
                fc = FunctionalCategory.objects.filter( area=item['fc_code'][0:1],
                                                        policy=item['fc_code'][0:2],
                                                        function=item['fc_code'][0:3],
                                                        programme=item['fc_code'],
                                                        budget=budget)
                if not fc:
                    print u"ALERTA: No se encuentra la categoría funcional '%s' para '%s': %s€" % (item['fc_code'].decode("utf8"), item['description'].decode("utf8"), item['amount']/100)
                    continue
                else:
                    fc = fc[0]
            else:
                fc = dummy_fc

            BudgetItem(institutional_category=ic,
                      functional_category=fc,
                      economic_category=ec,
                      funding_category=dummy_fdc,
                      item_number=item.get('item_number', ''),
                      expense=item['is_expense'],
                      actual=item['is_actual'],
                      amount=item['amount'],
                      description=item['description'],
                      budget=budget).save()

        if budgeted_income != budgeted_expense:
            print "  Info: los ingresos y gastos del presupuesto no coinciden %0.2f <> %0.2f" % (budgeted_income/100.0, budgeted_expense/100.0)


    # Load the institutional categories
    def load_institutional_classification(self, path, budget):
        reader = csv.reader(open(os.path.join(path, '..', '..', 'clasificacion_organica.csv'), 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):  # Ignore comments
                continue

            institution = line[0]
            section = line[1]
            department = line[2]
            description = line[3]

            ic = InstitutionalCategory( institution=institution if institution != "" else None,
                                        section=institution+section if section != "" else None,
                                        department=institution+section+department if department != "" else None,
                                        description=description,
                                        budget=budget)
            ic.save()


    # Load the economic categories
    def load_economic_classification(self, path, budget):
        reader = csv.reader(open(os.path.join(path, '..', '..', 'clasificacion_economica.csv'), 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):  # Ignore comments
                continue

            is_expense = (line[0] != 'I')
            chapter = line[1]
            article = line[2]
            concept = line[3]
            description = line[4]

            ec = EconomicCategory(  expense=is_expense,
                                    chapter=chapter if chapter != "" else None,
                                    article=chapter+article if article != "" else None,
                                    heading=chapter+article+concept if concept != "" else None,
                                    description=description,
                                    budget=budget)
            ec.save()


    # Load the functional categories
    def load_functional_classification(self, path, budget):
        reader = csv.reader(open(os.path.join(path, '..', '..', 'areas_funcionales.csv'), 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):     # Ignore comments
                continue

            area = line[0]
            policy = line[1]
            group = line[2]
            programme = line[3]
            description = line[4]

            fc = FunctionalCategory(area=area if area != "" else None,
                                    policy=area+policy if policy != "" else None,
                                    function=area+policy+group if group != "" else None,
                                    programme=area+policy+group+programme if programme != "" else None,
                                    description=description,
                                    budget=budget)
            fc.save()


    # Read number in English format (123,456.78), and return as number of cents
    def _read_english_number(self, s):
        if (s.strip()==""):
            return 0

        return int(Decimal(s.replace(',', ''))*100)

    # Get the amount for a budget line. 
    # This method is here mostly to support easy overloading in child classes
    def _parse_amount(self, amount):
        return self._read_english_number(amount)

