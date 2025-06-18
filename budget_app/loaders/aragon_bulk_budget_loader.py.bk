# -*- coding: UTF-8 -*-
from budget_app.models import *
from collections import namedtuple
from decimal import *
import csv
import os
import re

class AragonBulkBudgetLoader:
    BudgetId = namedtuple('BudgetId', 'entity_id year')
    Uid = namedtuple('Uid', 'dimension is_expense is_actual chapter article concept subconcept')
    Item = namedtuple('Item', 'description amount')
    FunctionalId = namedtuple('FunctionalId', 'policy group function')

    has_budget_data = {}
    has_actual_data = {}
    functional_areas = {}

    def load(self, level, path):
        # Parse the incoming data and keep in memory
        budget_items = {}

        economic_filename = os.path.join(path, 'clasificacion_economica.csv')
        self.parse_budget_data(budget_items, level, economic_filename)
        non_xbrl_filename = os.path.join(path, 'no_xbrl.csv')
        self.parse_non_xbrl_data(budget_items, level, non_xbrl_filename)

        functional_filename = os.path.join(path, 'clasificacion_funcional.csv')
        self.parse_budget_data(budget_items, level, functional_filename)

        self.load_functional_area_fix(path)

        # Now load the data one budget at a time
        for budget_id in budget_items:
            self.load_budget(level, path, budget_id.entity_id, budget_id.year, budget_items[budget_id])

    def parse_budget_data(self, budget_items, level, filename):
        # Group the incoming data (unsorted, and involving many different entities) by year/entity
        # Note: Since the structure of the incoming data is still changing at this time, and usually
        # the data comes in a per-year-per-entity, it feels better to load data this way, allowing
        # us to accomodate later on data files with only subsets of the overall domain.
        reader = csv.reader(open(filename, 'rb'), delimiter=';')
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):         # Ignore comments
                continue

            if re.match("^ +$", line[0]):       # Ignore empty lines
                continue

            if not re.match("^   ", line[0]):   # Ignore lines with SQL commands
                continue

            # Sigh. Deal with slightly different formats
            # if level == 'municipio' and 'clasificacion_economica.csv' in filename:  # Remove budget id
            #     line.pop(0)
            if level == 'municipio':    # Remove province id
                line[4] = line[3].strip()+line[4].strip()
                line.pop(3)

            # Ignore data before 2011, the one we have is crappy
            year = line[0].strip()
            if (int(year) < 2011):
                continue

            # Ignore chapter 0 data, which is sometimes present as a sum of the other chapters.
            # If it was always there, and was correct, we could use it to validate the data we're loading
            # but it's not the case: 99% of the time missing, and when present often nonsense. If we
            # left it in it'd create mayhem when present, because we'd double count it.
            chapter = line[5].strip()
            if (chapter == '0'):
                continue

            # Ignore zero amounts. We used to do this when inserting into the DB, but it's useful to 
            # know it at this point, so we can fall back into non-XBRL data if needed. There's a
            # bit of duplication, calculating the amount twice, but, good enough.
            amount = self._get_amount(line)
            if amount == 0:
                continue

            # Finally, we have useful data
            budget_id = AragonBulkBudgetLoader.BudgetId(line[3], year)
            if not budget_id in budget_items:
                budget_items[budget_id] = []
            budget_items[budget_id].append(line)

            # Keep track of what we have
            if self._is_actual(line):
                AragonBulkBudgetLoader.has_actual_data[budget_id] = True
            else:
                AragonBulkBudgetLoader.has_budget_data[budget_id] = True


    def parse_non_xbrl_data(self, budget_items, level, filename):
        reader = csv.reader(open(filename, 'rb'), delimiter=';')
        for index, line in enumerate(reader):
            if re.match("^[A-Z]+", line[0]):    # Ignore title
                continue

            if re.match("^ +$", line[0]):       # Ignore empty lines
                continue

            if re.match("^ +$", line[2]):       # Ignore lines with empty years (sigh)
                continue

            # Ignore data before 2011, the one we have is crappy
            year = line[2].strip()
            if (int(year) < 2011):
                continue

            # Retrieve entity id
            if level == 'municipio':
                entity_name = line[83]          # not really used, but handy
                entity_id = line[84]
            else:
                entity_name = line[81]          # not really used, but handy
                entity_id = line[82]
            if ( len(entity_id)<2 ):            # Zero padding county codes
                entity_id = "0"+entity_id

            # Retrieve economic data
            income_budget = line[3:12]
            expense_budget = line[12:21]
            income_actual = line[21:30]
            expense_actual = line[30:39]

            # Convert it to the XBRL data format, and store it for further processing.
            # Note that we only use this data if the more detailed one coming via XBRL
            # (which we have loaded already in this very same script) does not exist.
            budget_id = AragonBulkBudgetLoader.BudgetId(entity_id, year)
            if not budget_id in budget_items:
                budget_items[budget_id] = []
                budget_items[budget_id].extend(self.non_xbrl_summary_as_lines(income_budget, 'I', 'PRESUPUESTO'))
                budget_items[budget_id].extend(self.non_xbrl_summary_as_lines(expense_budget, 'G', 'PRESUPUESTO'))
                budget_items[budget_id].extend(self.non_xbrl_summary_as_lines(income_actual, 'I', 'LIQUIDACION'))
                budget_items[budget_id].extend(self.non_xbrl_summary_as_lines(expense_actual, 'G', 'LIQUIDACION'))

                # Keep track of what we have
                AragonBulkBudgetLoader.has_actual_data[budget_id] = True
                AragonBulkBudgetLoader.has_budget_data[budget_id] = True


    # Convert a non-XBRL one-line summary into an array of lines matching the format of 
    # the XBRL data files
    def non_xbrl_summary_as_lines(self, data_items, is_expense, is_actual):
        lines = []
        for index, line in enumerate(data_items):
            chapter = str(index+1)
            lines.append([
                None,                   # year, not used onwards
                is_expense,
                is_actual,
                None,                   # entity id, not used
                None,                   # entity name, not used
                chapter,
                "",                     # article
                "",                     # concept
                "",                     # subconcept
                "Capítulo "+chapter,
                "",
                data_items[index],      # amount for budget lines
                data_items[index]       # amount for execution budget lines
            ])
        return lines


    def load_budget(self, level, path, entity_id, year, items):
        # Find the public body the budget relates to
        entity = Entity.objects.filter(level=level, code=entity_id)
        if not entity:
            raise Exception("Entity (%s/%s) not found" % (level, entity_id))
        else:
            entity = entity[0]
#        print u"Cargando presupuesto para entidad '%s' año %s..." % (entity.name, year)

        # Check whether the budget exists already
        budget = Budget.objects.filter(entity=entity, year=year)
        if not budget:
            # Create the budget if needed in the database
            budget = Budget(entity=entity, year=year)
            budget.save()

            # Load the economic and functional classification from a manually edited file
            # XXX: Could we share this across budgets?
            self.load_economic_classification(path, budget)
            self.load_functional_classification(path, budget)

        else:
            budget = budget[0]

            # Delete previous budget for the given entity/year if it exists
            budget_id = AragonBulkBudgetLoader.BudgetId(entity_id, year)
            if budget_id in AragonBulkBudgetLoader.has_budget_data:
                BudgetItem.objects.filter(budget=budget, actual=False).delete()
            if budget_id in AragonBulkBudgetLoader.has_actual_data:
                BudgetItem.objects.filter(budget=budget, actual=True).delete()

        # Process the budget item
        # We can't just go ahead and store it, since the incoming data has subtotals, so we
        # need to avoid double counting amounts
        budget_items = {}
        for item in items:
            dimension = self._get_dimension(item)
            is_expense = (item[1].strip() == 'G' or dimension == 'Functional')
            is_actual = self._is_actual(item)
            chapter = item[5].strip()
            article = item[6].strip()
            concept = item[7].strip()
            subconcept = item[8].strip()
            description = item[9].strip()

            amount = self._get_amount(item)
            if amount == 0:
                continue

            # We are missing the area value in the functional data (almost always, there's 'P' instead)
            if dimension == 'Functional' and chapter == 'P':
                description = description.replace("   =", "   ").strip()    # Sigh, random extra '=' in input
                chapter = AragonBulkBudgetLoader.functional_areas.get(description.lower().replace(' ',''),'')
                if chapter=='':
                    print u"ALERTA: No se encuentra el area funcional para '%s': %s€" % (description.decode("utf8"), amount)
                    continue

            uid = AragonBulkBudgetLoader.Uid(dimension, is_expense, is_actual, chapter, article, concept, subconcept)
            self.keep_budget_item(budget_items, uid, description, amount)

        self.load_budget_items(budget, budget_items)


    def load_budget_items(self, budget, budget_items):
        # Since the incoming data is not fully classified along the four dimensions we defined
        # for the main budget (Aragón, the good one), we are forced to assign the items a 
        # catch-all fake category. (Leaving the category blank would be another possibility,
        # but we'd have to modify the DB structure for that, and also our breakdown queries,
        # so I'm going this slightly hackier way first.)
        # Having null values will make items don't show up when breaking down along those
        # levels. Be careful though, some fields are not nullable, so I'm putting an 'X'
        # there; should check whether they could be made nullable.
        dummy_ic = InstitutionalCategory( institution='X',
                                    section=None,
                                    department=None,
                                    description='Desconocido',
                                    budget=budget)
        dummy_ic.save()
        dummy_ec = EconomicCategory(expense=True,   # True/False doesn't really matter
                                    chapter='X',
                                    article=None,
                                    heading=None,
                                    subheading=None,
                                    description='Desconocido',
                                    budget=budget)
        dummy_ec.save()
        dummy_fc = FunctionalCategory(  area='X',
                                        policy=None,
                                        function=None,
                                        programme=None,
                                        description='Desconocido',
                                        budget=budget)
        dummy_fc.save()
        dummy_fdc = FundingCategory(expense=True,   # True/False doesn't really matter
                                    source='X',
                                    fund_class=None,
                                    fund=None,
                                    description='Desconocido',
                                    budget=budget)
        dummy_fdc.save()

        # Store data in the database
        budgeted_income = 0
        budgeted_expense = 0
        for uid in budget_items:
            item = budget_items[uid]
            if item.amount == 0:     # Can happen at this point, for subtotals, now deduplicated
                continue

            # Check whether budget income and expense match
            if uid.dimension == 'Economic' and not uid.is_actual:
                if uid.is_expense:
                    budgeted_expense += item.amount
                else:
                    budgeted_income += item.amount

            # Sometimes we get functional data, sometimes economic
            ec = dummy_ec
            fc = dummy_fc
            description = item.description
            if uid.dimension == 'Economic':
                ec = EconomicCategory.objects.filter(expense=uid.is_expense,
                                                    chapter=uid.chapter if uid.chapter != "" else None,
                                                    article=uid.chapter+uid.article if uid.article != "" else None,
                                                    heading=uid.chapter+uid.article+uid.concept if uid.concept != "" else None,
                                                    subheading=uid.chapter+uid.article+uid.concept+uid.subconcept if uid.subconcept != "" else None,
                                                    budget=budget)
                if not ec:
                    print u"ALERTA: No se encuentra la categoría económica '%s' para '%s': %s€" % (uid, item.description.decode("utf8"), item.amount)
                    continue
                else:
                    ec = ec[0]

                # Replace the ugly input descriptions with the manually-curated ones.
                # (This makes sense because each line in the input is a different economic category,
                # in a way we only have headings in the input, not items.)
                description = ec.description
            else:
                fc = FunctionalCategory.objects.filter(area=uid.chapter if uid.chapter != "" else None,
                                                        policy=uid.chapter+uid.article if uid.article != "" else None,
                                                        function=uid.chapter+uid.article+uid.concept if uid.concept != "" else None,
                                                        programme=uid.chapter+uid.article+uid.concept+uid.subconcept if uid.subconcept != "" else None,
                                                        budget=budget)
                if not fc:
                    print u"ALERTA: No se encuentra la categoría económica '%s' para '%s': %s€" % (uid, item.description.decode("utf8"), item.amount)
                    continue
                else:
                    fc = fc[0]

                # Replace the ugly input descriptions with the manually-curated ones.
                # (This makes sense because each line in the input is a different functional category,
                # in a way we only have headings in the input, not items.)
                description = fc.description


            BudgetItem(institutional_category=dummy_ic,
                      functional_category=fc,
                      economic_category=ec,
                      funding_category=dummy_fdc,
                      expense=uid.is_expense,
                      actual=uid.is_actual,
                      amount=item.amount,
                      description=description,
                      budget=budget).save()

        if budgeted_income != budgeted_expense:
            print "  Info: los ingresos y gastos del presupuesto no coinciden %0.2f <> %0.2f" % (budgeted_income/100.0, budgeted_expense/100.0)


    # Keep track of a new found budget item, do some validation and 
    # amend parent categories if needed
    def keep_budget_item(self, items, uid, description, amount):
        if uid in items:
            print "ALERTA: concepto repetido (%s). Tenía %s, ahora %s." % (uid, items[uid], amount)
            return

        # Add the item
        items[uid] = AragonBulkBudgetLoader.Item(description, amount)

        # Remove parent data, since the input data contains subtotals *sigh*
        if uid.subconcept != '':
            uid = AragonBulkBudgetLoader.Uid(uid.dimension, uid.is_expense, uid.is_actual, uid.chapter, uid.article, uid.concept, '')
            if uid in items:
                newAmount = AragonBulkBudgetLoader.Item(items[uid].description, items[uid].amount-amount)
                # Negative amounts are usually (always?) sign of invalid data. Alert about it, but go on
                if newAmount.amount < 0:
                    print "  Info: cantidad negativa '%s': %s" % (newAmount.description, newAmount.amount/100)
                items[uid] = newAmount
            else:
                print "  Info: Falta el subtotal para '%s': %s" % (description, amount/100)

        else:
            if uid.concept != '':
                uid = AragonBulkBudgetLoader.Uid(uid.dimension, uid.is_expense, uid.is_actual, uid.chapter, uid.article, '', '')
                if uid in items:
                    newAmount = AragonBulkBudgetLoader.Item(items[uid].description, items[uid].amount-amount)
                    if newAmount.amount < 0:
                        print "  Info: cantidad negativa '%s': %s" % (newAmount.description, newAmount.amount/100)
                    items[uid] = newAmount
                else:
                    print "  Info: Falta el subtotal para '%s': %s" % (description, amount/100)

            else:
                if uid.article != '':
                    uid = AragonBulkBudgetLoader.Uid(uid.dimension, uid.is_expense, uid.is_actual, uid.chapter, '', '', '')
                    if uid in items:
                        newAmount = AragonBulkBudgetLoader.Item(items[uid].description, items[uid].amount-amount)
                        if newAmount.amount < 0:
                            print "  Info: cantidad negativa '%s': %s" % (newAmount.description, newAmount.amount/100)
                        items[uid] = newAmount
                    else:
                        print "  Info: Falta el subtotal para '%s': %s" % (description, amount/100)


    # Load a manually improved version of the economic categories classification
    def load_economic_classification(self, path, budget):
        reader = csv.reader(open(os.path.join(path, '..', '..', 'clasificacion_economica.csv'), 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):  # Ignore comments
                continue

            is_expense = (line[0] != 'I')
            chapter = line[1]
            article = line[2]
            concept = line[3]
            subconcept = line[4]
            # We're slowly building our 'manually tuned' descriptions next to original ones
            description = line[6] if len(line) > 6 and line[6] != "" else line[5]

            ec = EconomicCategory(  expense=is_expense,
                                    chapter=chapter if chapter != "" else None,
                                    article=chapter+article if article != "" else None,
                                    heading=chapter+article+concept if concept != "" else None,
                                    subheading=chapter+article+concept+subconcept if subconcept != "" else None,
                                    description=description,
                                    budget=budget)
            ec.save()


    # Load a manually improved version of the functional categories classification.
    def load_functional_classification(self, path, budget):
        reader = csv.reader(open(os.path.join(path, '..', '..', 'areas_funcionales.csv'), 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):     # Ignore comments
                continue

            area = line[0]
            policy = line[1]
            group = line[2]
            # We're slowly building our 'manually tuned' descriptions next to original ones
            description = line[4] if len(line) > 4 and line[4] != "" else line[3]

            fc = FunctionalCategory(area=area if area != "" else None,
                                    policy=area+policy if policy != "" else None,
                                    function=area+policy+group if group != "" else None,
                                    description=description,
                                    budget=budget)
            fc.save()


    def load_functional_area_fix(self, path):
        reader = csv.reader(open(os.path.join(path, '..', '..', 'areas_funcionales.csv'), 'rb'))
        for index, line in enumerate(reader):
            if re.match("^#", line[0]):     # Ignore comments
                continue

            area = line[0]

            # Unfortunately the data we currently have is missing the area column, so we've rebuilt it
            # using this budget we found in Google :/ and need to jump through some extra hoops.
            # http://www.ayora.es/ayuntamiento/index.php/ayuntamiento/hacienda/presupuestos-municipales-2013/doc_download/376-pg1307-estado-de-gastos-clasificacion-por-programas-desglose-por-partidas
            AragonBulkBudgetLoader.functional_areas[line[3].lower()] = area


    # Read number in Spanish format (123.456,78), and return as number of cents
    # Note: I used to convert to float and multiply by 100, but that would result in a few cents off
    # (in a 5000 million € budgets). We now instead check for a comma and based on that multiply by 100
    # or not, but always as integer. 
    # TODO: Duplicated on budget_loader. Refactor
    def _read_spanish_number(self, s):
        # Some fields are blank in the municipal non-XBRL budget data
        if (s.strip()==""):
            return 0

        comma = s.find(',')

        if (comma>0 and comma < len(s) - 3):  # More than two significant positions. Alert, shouldn't happen
            print u"ALERTA: Demasiados decimales en '%s'. Ignorando..." % (s)
            return 0

        if (comma>0 and comma == len(s) - 3):
            return int(s.replace('.', '').replace(',', ''))
        else:
            if (comma>0 and comma == len(s) - 2):
                return int(s.replace('.', '').replace(',', '')) * 10
            else:   # No comma, or trailing comma (yes, it happens)
                return int(s.replace('.', '')) * 100


    # Returns the classification dimension of a given budget line: economic or functional
    def _get_dimension(self, item):
        return 'Functional' if item[1].strip() == 'F' else 'Economic'


    # Whether a budget line refers to a projected (budget) or actual amount (execution)
    def _is_actual(self, item):
        return (item[2].strip() == 'LIQUIDACION')


    # Get the amount for a budget line, trickier than you may think
    def _get_amount(self, item):
        if self._get_dimension(item) == 'Functional':
            # Add all columns, except the last two: the last one is always zero, and the next
            # to last contains some numbers whose meaning at this point is unclear (!?).
            # If we remove the next to last column, then the economic and functional 
            # breakdowns on the expense side match. Good news.
            amount = 0
            for i in range(11, len(item)-2):
                if item[i]:
                    amount += self._read_spanish_number(item[i])
        else:
            if self._is_actual(item):
                # So I figured out the first column in execution data is the final budget
                amount = self._read_spanish_number(item[12])
            else:
                amount = self._read_spanish_number(item[11])

        return amount

