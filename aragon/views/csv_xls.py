# -*- coding: UTF-8 -*-

from django.http import HttpResponse
from aragon.models import Entity
from aragon.views import policies, policies_show, programmes_show, income_articles_show, expense_articles_show
from aragon.views import entities_index, entities_show, entities_show_article, entities_show_policy
from helpers import get_context
import csv
import xlwt


#
# ENTITY BREAKDOWNS
#
def write_entity_functional_breakdown(c, writer):
    writer.writerow(['#Año', 'Id Política', 'Nombre Política', 'Id Programa', 'Nombre Programa', 'Presupuesto Gasto', 'Gasto Real'])
    for policy_id, policy in c['functional_breakdown'].subtotals.iteritems():
        # If we are missing the lower levels of the breakdown, we need to massage the data a bit.
        items = policy.subtotals
        if len(policy.subtotals) == 0:
            items = {'': policy}
        # Iterate through all the items
        for programme_id, programme in items.iteritems():
            for year in set(programme.years.values()):
                budget_column_name = str(year)
                actual_column_name = 'actual_'+str(year)
                total_expense = programme.total_expense

                if not total_expense.get(budget_column_name) and not total_expense.get(actual_column_name):
                    continue

                values = [
                    year,
                    policy_id,
                    c['descriptions']['functional'].get(policy_id, '').encode("utf-8"),
                    programme_id,
                    c['descriptions']['functional'].get(programme_id, '').encode("utf-8"),
                    # The original amounts are in cents:
                    total_expense[budget_column_name] / 100.0 if budget_column_name in total_expense else None,
                    total_expense[actual_column_name] / 100.0 if actual_column_name in total_expense else None
                ]
                writer.writerow(values)

def write_entity_economic_breakdown(c, field, writer):
    field_username = 'Gastos' if field == 'expense' else 'Ingresos'
    writer.writerow(['#Año', 'Id Artículo', 'Nombre Artículo', 'Id Concepto', 'Nombre Concepto', 'Presupuesto '+field_username, field_username+' Reales'])
    for article_id, article in c['economic_breakdown'].subtotals.iteritems():
        for heading_id, heading in article.subtotals.iteritems():
            for year in set(heading.years.values()):
                budget_column_name = str(year)
                actual_column_name = 'actual_'+str(year)
                totals = heading.total_expense if field == 'expense' else heading.total_income

                if not totals.get(budget_column_name) and not totals.get(actual_column_name):
                    continue

                values = [
                    year,
                    article_id,
                    c['descriptions'][field].get(article_id, '').encode("utf-8"),
                    heading_id,
                    c['descriptions'][field].get(heading_id, '').encode("utf-8"),
                    # The original amounts are in cents:
                    totals[budget_column_name] / 100.0 if budget_column_name in totals else None,
                    totals[actual_column_name] / 100.0 if actual_column_name in totals else None
                ]
                writer.writerow(values)

def write_entity_economic_expense_breakdown(c, writer):
    return write_entity_economic_breakdown(c, 'expense', writer)

def write_entity_income_breakdown(c, writer):
    return write_entity_economic_breakdown(c, 'income', writer)

def entity_expenses(request, level, slug, format):
    c = get_context(request)
    entity = Entity.objects.get(level=level, slug=slug)
    return entities_show(request, c, entity, _generator('gastos-%s-%s' % (level, slug), format, write_entity_economic_expense_breakdown))

def entity_fexpenses(request, level, slug, format):
    c = get_context(request)
    entity = Entity.objects.get(level=level, slug=slug)
    return entities_show(request, c, entity, _generator('gastosf-%s-%s' % (level, slug), format, write_entity_functional_breakdown))

def entity_income(request, level, slug, format):
    c = get_context(request)
    entity = Entity.objects.get(level=level, slug=slug)
    return entities_show(request, c, entity, _generator('ingresos-%s-%s' % (level, slug), format, write_entity_income_breakdown))



#
# FUNCTIONAL BREAKDOWN
#
def write_functional_breakdown(c, writer):
    writer.writerow(['#Año', 'Id Política', 'Nombre Política', 'Id Programa', 'Nombre Programa', 'Presupuesto Gastos', 'Gastos Reales'])
    for programme_id, programme in c['functional_breakdown'].subtotals.iteritems():
        for year in set(programme.years.values()):
            budget_column_name = str(year)
            actual_column_name = 'actual_'+str(year)
            total_expense = programme.total_expense

            if not total_expense.get(budget_column_name) and not total_expense.get(actual_column_name):
                continue

            values = [
                year,
                c['policy_uid'],
                c['descriptions']['functional'].get(c['policy_uid'], '').encode("utf-8"),
                programme_id,
                c['descriptions']['functional'].get(programme_id, '').encode("utf-8"),
                # The original amounts are in cents:
                total_expense[budget_column_name] / 100.0 if budget_column_name in total_expense else None,
                total_expense[actual_column_name] / 100.0 if actual_column_name in total_expense else None
            ]
            writer.writerow(values)

def functional_policy_breakdown(request, id, format):
    return policies_show(request, id, '', _generator("%s.funcional" % id, format, write_functional_breakdown))

def functional_article_breakdown(request, id, format):
    return expense_articles_show(request, id, format, _generator("%s.economica" % id, format, write_entity_functional_breakdown))

def entity_article_fexpenses(request, level, slug, id, format):
    c = get_context(request)
    entity = Entity.objects.get(level=level, slug=slug)
    return entities_show_policy(request, c, entity, id, '', _generator('gastosf-%s-%s-%s' % (level, slug, id), format, write_entity_functional_breakdown))


#
# ECONOMIC BREAKDOWN
#
def write_economic_breakdown(c, writer):
    writer.writerow(['#Año', 'Id Capítulo', 'Nombre Capítulo', 'Id Artículo', 'Nombre Artículo', 'Id Concepto', 'Nombre Concepto', 'Presupuesto Gastos', 'Gastos Reales'])
    for chapter_id, chapter in c['economic_breakdown'].subtotals.iteritems():
        for article_id, article in chapter.subtotals.iteritems():
            for heading_id, heading in article.subtotals.iteritems():
                for year in set(heading.years.values()):
                    budget_column_name = str(year)
                    actual_column_name = 'actual_'+str(year)
                    total_expense = heading.total_expense

                    if not total_expense.get(budget_column_name) and not total_expense.get(actual_column_name):
                        continue

                    values = [
                        year,
                        chapter_id,
                        c['descriptions']['expense'].get(chapter_id, '').encode("utf-8"),
                        article_id,
                        c['descriptions']['expense'].get(article_id, '').encode("utf-8"),
                        heading_id,
                        c['descriptions']['expense'].get(heading_id, '').encode("utf-8"),
                        total_expense[budget_column_name] / 100.0 if budget_column_name in total_expense else None,
                        total_expense[actual_column_name] / 100.0 if actual_column_name in total_expense else None
                    ]
                    writer.writerow(values)

def economic_policy_breakdown(request, id, format):
    return policies_show(request, id, '', _generator("%s.economica" % id, format, write_economic_breakdown))

def economic_programme_breakdown(request, id, format):
    return programmes_show(request, id, '', _generator("%s.economica" % id, format, write_economic_breakdown))


#
# ECONOMIC ARTICLE BREAKDOWN
#
def write_economic_article_breakdown(c, field, writer):
    field_username = 'Gastos' if field == 'expense' else 'Ingresos'
    writer.writerow(['#Año', 'Id Artículo', 'Nombre Artículo', 'Id Concepto', 'Nombre Concepto', 'Id Subconcepto', 'Nombre Subconcepto', 'Presupuesto '+field_username, field_username+' Reales'])
    for heading_id, heading in c['economic_breakdown'].subtotals.iteritems():
        for item_uid, item in heading.subtotals.iteritems():
            for year in set(item.years.values()):
                budget_column_name = str(year)
                actual_column_name = 'actual_'+str(year)
                totals = item.total_expense if field == 'expense' else item.total_income

                if not totals.get(budget_column_name) and not totals.get(actual_column_name):
                    continue

                values = [
                    year,
                    c['article_id'],
                    c['descriptions'][field].get(c['article_id'], '').encode("utf-8"),
                    heading_id,
                    c['descriptions'][field].get(heading_id, '').encode("utf-8"),
                    item_uid,
                    c['descriptions'][field].get(item_uid, '').encode("utf-8"),
                    # The original amounts are in cents:
                    totals[budget_column_name] / 100.0 if budget_column_name in totals else None,
                    totals[actual_column_name] / 100.0 if actual_column_name in totals else None
                ]
                writer.writerow(values)

def write_economic_article_expense_breakdown(c, writer):
    return write_economic_article_breakdown(c, 'expense', writer);

def write_economic_article_income_breakdown(c, writer):
    return write_economic_article_breakdown(c, 'income', writer);

def economic_article_breakdown(request, id, format):
    return income_articles_show(request, id, format, _generator("%s.economica" % id, format, write_economic_article_income_breakdown))

def entity_article_expenses(request, level, slug, id, format):
    c = get_context(request)
    entity = Entity.objects.get(level=level, slug=slug)
    return entities_show_article(request, c, entity, id, '', 'expense', _generator('ingresos-%s-%s-%s' % (level, slug, id), format, write_economic_article_expense_breakdown))

def entity_article_income(request, level, slug, id, format):
    c = get_context(request)
    entity = Entity.objects.get(level=level, slug=slug)
    return entities_show_article(request, c, entity, id, '', 'income', _generator('ingresos-%s-%s-%s' % (level, slug, id), format, write_economic_article_income_breakdown))


#
# FUNDING BREAKDOWN
#
def write_funding_breakdown(c, writer):
    field_username = 'Gastos' if c['show_side'] == 'expense' else 'Ingresos'
    writer.writerow(['#Año', 'Id Fuente', 'Nombre Fuente', 'Id Fondo', 'Nombre Fondo', 'Presupuesto '+field_username, field_username+' Reales'])
    for source_id, source in c['funding_breakdown'].subtotals.iteritems():
        for fund_id, fund in source.subtotals.iteritems():
            for year in set(fund.years.values()):
                budget_column_name = str(year)
                actual_column_name = 'actual_'+str(year)
                totals = fund.total_expense if c['show_side'] == 'expense' else fund.total_income

                if not totals.get(budget_column_name) and not totals.get(actual_column_name):
                    continue

                values = [
                    year,
                    source_id,
                    c['descriptions']['funding'].get(source_id, '').encode("utf-8"),
                    fund_id,
                    c['descriptions']['funding'].get(fund_id, '').encode("utf-8"),
                    # The original amounts are in cents:
                    totals[budget_column_name] / 100.0 if budget_column_name in totals else None,
                    totals[actual_column_name] / 100.0 if actual_column_name in totals else None
                ]
                writer.writerow(values)

def funding_policy_breakdown(request, id, format):
    return policies_show(request, id, '', _generator("%s.financiacion" % id, format, write_funding_breakdown))

def funding_programme_breakdown(request, id, format):
    return programmes_show(request, id, '', _generator("%s.financiacion" % id, format, write_funding_breakdown))

def funding_article_breakdown(request, id, format):
    return income_articles_show(request, id, '', _generator("%s.financiacion" % id, format, write_funding_breakdown))


#
# INSTITUTIONAL BREAKDOWN
#
def write_institutional_breakdown(c, writer):
    field_username = 'Gastos' if c['show_side'] == 'expense' else 'Ingresos'
    writer.writerow(['#Año', 'Nombre Sección', 'Nombre Departamento', 'Presupuesto '+field_username, field_username+' Reales'])
    for section_id, section in c['institutional_breakdown'].subtotals.iteritems():
        for department_id, department in section.subtotals.iteritems():
            for year in set(department.years.values()):
                budget_column_name = str(year)
                actual_column_name = 'actual_'+str(year)
                totals = department.total_expense if c['show_side'] == 'expense' else department.total_income

                if not totals.get(budget_column_name) and not totals.get(actual_column_name):
                    continue

                values = [
                    year,
                    c['descriptions']['institutional'].get(section_id, '').encode("utf-8"),
                    c['descriptions']['institutional'].get(department_id, '').encode("utf-8"),
                    # The original amounts are in cents:
                    totals[budget_column_name] / 100.0 if budget_column_name in totals else None,
                    totals[actual_column_name] / 100.0 if actual_column_name in totals else None
                ]
                writer.writerow(values)

def institutional_policy_breakdown(request, id, format):
    return policies_show(request, id, '', _generator("%s.organica" % id, format, write_institutional_breakdown))

def institutional_programme_breakdown(request, id, format):
    return programmes_show(request, id, '', _generator("%s.organica" % id, format, write_institutional_breakdown))

def institutional_article_breakdown(request, id, format):
    return income_articles_show(request, id, '', _generator("%s.organica" % id, format, write_institutional_breakdown))


#
# ENTITIES LISTS
#
def write_entities_breakdown(c, field, writer):
    field_username = 'Gastos' if field == 'expense' else 'Ingresos'
    writer.writerow(['#Año', 'Entidad', 'Presupuesto '+field_username, field_username+' Reales'])
    for entity_id, entity in c['economic_breakdown'].subtotals.iteritems():
        for year in set(entity.years.values()):
            budget_column_name = str(year)
            actual_column_name = 'actual_'+str(year)
            totals = entity.total_expense if field == 'expense' else entity.total_income

            if not totals.get(budget_column_name) and not totals.get(actual_column_name):
                continue

            values = [
                year,
                entity_id.encode("utf-8"),
                # The original amounts are in cents:
                totals[budget_column_name] / 100.0 if budget_column_name in totals else None,
                totals[actual_column_name] / 100.0 if actual_column_name in totals else None
            ]
            writer.writerow(values)
    return

def write_entities_expenses_breakdown(c, writer):
    return write_entities_breakdown(c, 'expenses', writer)

def entities_expenses(request, level, format):
    return entities_index(request, get_context(request), level, _generator('gastos_%ss' % level, format, write_entities_expenses_breakdown))

def write_entities_income_breakdown(c, writer):
    return write_entities_breakdown(c, 'income', writer)

def entities_income(request, level, format):
    return entities_index(request, get_context(request), level, _generator('ingresos_%ss' % level, format, write_entities_income_breakdown))


#
# Helper classes to reuse CSV/Excel generation code
#
class CSVGenerator:
    def __init__(self, filename, content_generator):
        self.filename = filename
        self.content_generator = content_generator

    def generate_response(self, c):
        # Create the HttpResponse object with the appropriate CSV header
        response = HttpResponse(mimetype='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.filename

        writer = csv.writer(response)
        self.content_generator(c, writer)
        return response

class xlwtWorksheetWrapper:
    def __init__(self, worksheet):
        self.worksheet = worksheet
        self.current_row = 0

    def writerow(self, values):
        column = 0
        for value in values:
            self.worksheet.write(self.current_row, column, value)
            column += 1
        self.current_row += 1

class XLSGenerator:
    def __init__(self, filename, content_generator):
        self.filename = filename
        self.content_generator = content_generator

    def generate_response(self, c):
        response = HttpResponse(mimetype='application/ms-excel; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="%s"' % self.filename

        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Datos')
        self.content_generator(c, xlwtWorksheetWrapper(worksheet))
        workbook.save(response)
        return response

def _generator(filename, format, content_generator):
    if format == 'csv':
        return CSVGenerator('%s.%s' % (filename, format), content_generator)
    else:
        return XLSGenerator('%s.%s' % (filename, format), content_generator)
