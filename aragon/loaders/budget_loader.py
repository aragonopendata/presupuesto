# -*- coding: UTF-8 -*-
from aragon.models import *
import csv
import os.path


class BudgetLoader:
    def load(self, level, name, year, path):
        # Delete the existing budget if needed
        entity = self._get_entity(level, name)
        budget = Budget.objects.filter(entity=entity, year=year)
        if budget:
            budget.delete()

        print "Cargando presupuesto de %s..." % path
        budget = Budget(entity=entity, year=year)
        budget.save()
        self.load_institutional_hierarchy(budget, path)
        self.load_economic_hierarchy(budget, path)
        self.load_functional_hierarchy(budget, path)
        self.load_funding_hierarchy(budget, path)
        self.load_data_files(budget, path)

    def load_execution(self, level, name, year, path):
        entity = self._get_entity(level, name)
        budget = Budget.objects.filter(entity=entity, year=year)[0]

        print "Borrando ejecución presupuestaria previa..."
        BudgetItem.objects.filter(budget_id=budget, actual=True).delete()

        print "Cargando ejecución presupuestaria de %s..." % path
        self.load_execution_data_files(budget, path)

    def load_institutional_hierarchy(self, budget, path):
        institutions_filename = os.path.join(path, 'estructura_organica.csv')
        print "Cargando lista de secciones de %s..." % institutions_filename
        reader = csv.reader(open(institutions_filename, 'rb'), delimiter=';')
        for line in reader:
            if not line or line[0] == "" or line[0] == 'EJERCICIO':  # Ignore header or empty lines
                continue

            if budget.year != line[0]:
                raise Exception("Years should match (%s <> %s)" % (budget.year, line[0]))

            description = line[2] if line[3] == "" else line[3]
            description = unicode(description, encoding='unicode-escape')

            InstitutionalCategory(institution=line[1][0:2],
                                  section=(line[1][0:4] if len(line[1]) > 2 else None),
                                  department=(line[1] if len(line[1]) > 4 else None),
                                  description=description,
                                  budget=budget).save()

    def load_economic_hierarchy(self, budget, path):
        filename = os.path.join(path, 'estructura_economica.csv')
        print "Cargando jerarquía económica de %s..." % filename
        reader = csv.reader(open(filename, 'rb'), delimiter=';')
        for line in reader:
            if not line or line[0] == "" or line[0] == 'EJERCICIO':  # Ignore header or empty lines
                continue

            if budget.year != line[0]:
                raise Exception("Years should match (%s <> %s)" % (budget.year, line[0]))

            # Read the description. There are patches to the budget descriptions that are
            # more easily done here (although it's ugly to have these hardcoded things around).
            description = line[7]
            if description == 'Del Exterior':
                description = 'Fondos Europeos'
            description = unicode(description, encoding='unicode-escape')

            EconomicCategory(expense=(line[1].upper() == 'G'),
                              chapter=(line[2] if line[2] != "" else None),
                              article=(line[3] if line[3] != "" else None),
                              heading=(line[4] if line[4] != "" else None),
                              subheading=(line[5] if line[5] != "" else None),
                              description=description,
                              budget=budget).save()

    def load_funding_hierarchy(self, budget, path):
        filename = os.path.join(path, 'estructura_financiacion.csv')
        print "Cargando jerarquía de financiación de %s..." % filename
        reader = csv.reader(open(filename, 'rb'), delimiter=';')
        for line in reader:
            if not line or line[0] == "" or line[0] == 'EJERCICIO':  # Ignore header or empty lines
                continue

            if budget.year != line[0]:
                raise Exception("Years should match (%s <> %s)" % (budget.year, line[0]))

            # Prefer the long description if it exists, otherwise the short one
            description = line[6] if (line[6] != "") else line[5]
            description = unicode(description, encoding='unicode-escape')

            FundingCategory(expense=(line[1].upper() == 'G'),
                              source=(line[2] if line[2] != "" else None),
                              fund_class=(line[3] if line[3] != "" else None),
                              fund=(line[4] if line[4] != "" else None),
                              description=description.title(),
                              budget=budget).save()

    # Policies are grouped in four new areas defined by the client (because the original ones
    # are quite useless). It's easier to do it when loading the data, instead of modifying the 
    # original budget files, harder to track.
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

    def load_functional_hierarchy(self, budget, path):
        filename = os.path.join(path, 'estructura_funcional.csv')
        print "Cargando jerarquía funcional de %s..." % filename
        reader = csv.reader(open(filename, 'rb'), delimiter=';')
        for line in reader:
            if not line or line[0] == "" or line[0] == 'EJERCICIO':  # Ignore header or empty lines
                continue

            if line[2] == "":  # Don't load the areas, they want to override them
                continue

            if budget.year != line[0]:
                raise Exception("Years should match (%s <> %s)" % (budget.year, line[0]))

            # Read the description. There are patches to the budget descriptions that are
            # more easily done here (although it's ugly to have these hardcoded things around).
            description = line[6]
            if description == 'Salud Pública':
                description = 'Prevención de la Salud'
            description = unicode(description, encoding='unicode-escape')

            # We map the original policy into the four custom-made areas, as explained above.
            # We prepend all the children categories with the new area value so the visualizations
            # later know which area a policy or programme belongs to, as that's used to pick colors.
            policy = line[2]
            new_area = self._map_policy_to_new_area(policy)
            FunctionalCategory(area=new_area,
                                  policy=new_area + policy,
                                  function=(new_area + line[3] if line[3] != "" else None),
                                  programme=(new_area + line[4] if line[4] != "" else None),
                                  description=description.title(),
                                  budget=budget).save()

        # Create custom areas (I could put this in a file, but doesn't feel worth it)
        FunctionalCategory(area='0', policy=None, description='Deuda', budget=budget).save()
        FunctionalCategory(area='1', policy=None, description='Administración', budget=budget).save()
        FunctionalCategory(area='2', policy=None, description='Bienestar Social', budget=budget).save()
        FunctionalCategory(area='3', policy=None, description='Desarrollo Económico', budget=budget).save()

        # Income data in Aragon is not classified functionally, but we need every budget item to be classified
        # along all dimensions (at least for now), because of the way we denormalize/join the data in the app.
        # So we create a fake functional category that will contain all the income data.
        FunctionalCategory(area='X',
                            policy='XX',
                            function='XXX',
                            programme='XXXX',
                            description='Ingresos',
                            budget=budget).save()

    def load_data_files(self, budget, path):
        filename = os.path.join(path, 'gastos.csv')
        print "Cargando gastos de %s..." % filename
        self.load_data_file(budget, filename, True, False)

        filename = os.path.join(path, 'ingresos.csv')
        print "Cargando ingresos de %s..." % filename
        self.load_data_file(budget, filename, False, False)

    def load_execution_data_files(self, budget, path):
        filename = os.path.join(path, 'ejecucion_gastos.csv')
        print "Cargando ejecución de gastos de %s..." % filename
        self.load_data_file(budget, filename, True, True)

        filename = os.path.join(path, 'ejecucion_ingresos.csv')
        print "Cargando ejecución de ingresos de %s..." % filename
        self.load_data_file(budget, filename, False, True)

    def load_data_file(self, budget, filename, is_expense, is_actual):
        reader = csv.reader(open(filename, 'rb'), delimiter=';')
        for line in reader:
            if not line or line[0] == "" or line[0].upper() == 'EJERCICIO':  # Ignore header or empty lines
                continue

            if str(budget.year) != line[0]:
                if not is_actual:  # Be strict with budget data files
                    raise Exception(u"Los años no coinciden (%s <> %s)" % (budget.year, line[0]))
                else:
                    # Para la información de ejecución usamos el año del fichero, diga lo que diga
                    # la primera columna, pero informamos de ello por pantalla
                    print u"INFO: Usando el año %s para la línea [%s]" % (budget.year, line)

            # Add a null column for income data, so all the indexes below remain constant
            if not is_expense:
                line.insert(2, None)

            # Read the description first, as it's used in the error messages below
            description = line[5]
            description = unicode(description, encoding='unicode-escape')

            # For execution data, pick "Obligaciones/Créditos reconocidas/os"
            if is_actual:
                amount = line[10 if is_expense else 9]
            else:
                amount = line[6]

            # Match budget item data to existing categories
            ic_code = '0' + line[1] if len(line[1]) < 5 else line[1]  # Inconsistent 2012-2013
            ic = InstitutionalCategory.objects.filter(budget=budget,
                                            institution=ic_code[0:2],
                                            section=ic_code[0:4],
                                            department=ic_code)
            if not ic:
                print u"ALERTA: No se encuentra la institución '%s' para '%s': %s€" % (ic_code, description, amount)
                continue
            else:
                ic = ic[0]

            if is_expense:
                fc_code = '0' + line[2] if len(line[2]) < 4 else line[2]  # Inconsistent 2012-2013

                # See explanation above about the remapping of areas into four 'super-areas'
                policy = fc_code[0:2]
                new_area = self._map_policy_to_new_area(policy)
                fc = FunctionalCategory.objects.filter(budget=budget,
                                                    area=new_area,
                                                    policy=new_area + policy,
                                                    function=new_area + fc_code[0:3],
                                                    programme=new_area + fc_code)
                if not fc:
                    print u"ALERTA: No se encuentra la categoría funcional '%s' para '%s': %s€" % (fc_code, description, amount)
                    continue
                else:
                    fc = fc[0]
            else:
                # Income data in Aragon is not classified functionally, so we use the fake category we created before
                fc = FunctionalCategory.objects.filter(budget=budget, programme='XXXX')[0]

            ec = EconomicCategory.objects.filter(budget=budget,
                                                expense=is_expense,
                                                chapter=line[3][0],
                                                article=line[3][0:2],
                                                heading=line[3][0:3],
                                                subheading=line[3])
            if not ec:
                print u"ALERTA: No se encuentra la categoría económica '%s' para '%s': %s€" % (line[3], description, amount)
                continue
            else:
                ec = ec[0]

            fdc = FundingCategory.objects.filter(budget=budget,
                                                expense=is_expense,
                                                source=line[4][0],
                                                fund_class=line[4][0:2],
                                                fund=line[4])
            if not fdc:
                print u"ALERTA: No se encuentra la categoría de financiación '%s' para '%s': %s€" % (line[4], description, amount)
                continue
            else:
                fdc = fdc[0]

            # When there is no description for the budget_item take the one from the parent economic category
            if description == "":
                description = ec.description

            # Create the budget item
            if amount != "":
                BudgetItem(institutional_category=ic,
                          functional_category=fc,
                          economic_category=ec,
                          funding_category=fdc,
                          expense=is_expense,
                          actual=is_actual,
                          amount=self._read_spanish_number(amount),
                          description=description,
                          budget=budget).save()

    # Read number in Spanish format (123.456,78), and return as number of cents
    # Note: I used to convert to float and multiply by 100, but that would result in a few cents off
    # (in a 5000 million € budgets). We now instead check for a comma and based on that multiply by 100
    # or not, but always as integer. 
    def _read_spanish_number(self, s):
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

    def _get_entity(self, level, name):
        entity = Entity.objects.filter(level=level, name=name)[0]
        if not entity:
            raise Exception("Entity (%s/%s) not found" % (level, name))
        return entity