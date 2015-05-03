# -*- coding: UTF-8 -*-

from django.http import HttpResponse
from budget_app.models import Entity
from budget_app.views import policies, policies_show, programmes_show, income_articles_show, expense_articles_show
from budget_app.views import entities_index, entities_show, entities_show_article, entities_show_policy
from helpers import get_context
import csv
import xlwt


# Note that in these exports we include not only the items at the lowest level of detail 
# (i.e. the leaves), but also the mid-level subtotals. There's a reason for this:
# initially there was a clean and consistent budget (Aragon), where all policies and 
# articles were broken down to the same level of detail. And it was good. And we could
# output just the leaves knowing all the information was there. Then came the counties 
# and towns, with variable level of detail each year, and it got harder to know when 
# to output chapters and when articles, although theoretically it was still possible.
# Last came the national budget, where the level of detail depends on the entity publishing
# the data: so we have expense articles broken down to heading and subheading level for
# some parts [1], while the Social Security stops right at the article level [2]. So
# if you globally add the headings (12x) for a particular article (12) it doesn't add up.
# On the screen breakdowns we ensure the subtotal shown for article 12 is correct, and
# we need to make sure that happens on exported data files also. Hence the need for
# including the subtotals in the CSV/XLS files.
#
# [1]: http://www.sepg.pap.minhap.gob.es/Presup/PGE2013Ley/MaestroDocumentos/PGE-ROM/doc/HTM/N_13_E_V_1_101_1_1_2_2_112_1_2.HTM
# [2]: http://www.sepg.pap.minhap.gob.es/Presup/PGE2013Ley/MaestroDocumentos/PGE-ROM/doc/HTM/N_13_E_R_31_2_1_G_1_1_1312C_P.HTM

#
# ENTITY BREAKDOWNS
#
def write_entity_functional_breakdown(c, writer):
    writer.writerow(['#Año', 'Id Política', 'Nombre Política', 'Id Programa', 'Nombre Programa', 'Presupuesto Gasto', 'Gasto Real'])
    for year in set(c['functional_breakdown'].years.values()):
        for policy_id, policy in c['functional_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, policy, 'expense', [policy_id, None], c['descriptions']['functional'])
            for programme_id, programme in policy.subtotals.iteritems():
                write_breakdown_item(writer, year, programme, 'expense', [policy_id, programme_id], c['descriptions']['functional'])

def write_entity_economic_breakdown(c, field, writer):
    field_username = 'Gastos' if field == 'expense' else 'Ingresos'
    writer.writerow(['#Año', 'Id Artículo', 'Nombre Artículo', 'Id Concepto', 'Nombre Concepto', 'Presupuesto '+field_username, field_username+' Reales'])
    for year in set(c['economic_breakdown'].years.values()):
        for article_id, article in c['economic_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, article, field, [article_id, None], c['descriptions'][field])
            for heading_id, heading in article.subtotals.iteritems():
                write_breakdown_item(writer, year, heading, field, [article_id, heading_id], c['descriptions'][field])

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
    for year in set(c['functional_breakdown'].years.values()):
        for programme_id, programme in c['functional_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, programme, 'expense', [c['policy_uid'], programme_id], c['descriptions']['functional'])

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
    for year in set(c['economic_breakdown'].years.values()):
        for chapter_id, chapter in c['economic_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, chapter, 'expense', [chapter_id, None, None], c['descriptions']['expense'])
            for article_id, article in chapter.subtotals.iteritems():
                write_breakdown_item(writer, year, article, 'expense', [chapter_id, article_id, None], c['descriptions']['expense'])
                for heading_id, heading in article.subtotals.iteritems():
                    write_breakdown_item(writer, year, heading, 'expense', [chapter_id, article_id, heading_id], c['descriptions']['expense'])

def economic_policy_breakdown(request, id, format):
    return policies_show(request, id, '', _generator("%s.economica" % id, format, write_economic_breakdown))

def write_detailed_economic_breakdown(c, writer):
    writer.writerow(['#Año', 'Id Capítulo', 'Nombre Capítulo', 'Id Artículo', 'Nombre Artículo', 'Id Subconcepto', 'Nombre Subconcepto', 'Presupuesto Gastos', 'Gastos Reales'])
    for year in set(c['economic_breakdown'].years.values()):
        for chapter_id, chapter in c['economic_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, chapter, 'expense', [chapter_id, None, None], c['descriptions']['expense'])
            for article_id, article in chapter.subtotals.iteritems():
                write_breakdown_item(writer, year, article, 'expense', [chapter_id, article_id, None], c['descriptions']['expense'])
                for heading_id, heading in article.subtotals.iteritems():
                    for subheading_id, subheading in heading.subtotals.iteritems():
                        write_breakdown_item(writer, year, subheading, 'expense', [chapter_id, article_id, subheading_id], c['descriptions']['expense'])

def economic_programme_breakdown(request, id, format):
    return programmes_show(request, id, '', _generator("%s.economica" % id, format, write_detailed_economic_breakdown))


#
# ECONOMIC ARTICLE BREAKDOWN
#
def write_economic_article_breakdown(c, field, writer):
    field_username = 'Gastos' if field == 'expense' else 'Ingresos'
    writer.writerow(['#Año', 'Id Artículo', 'Nombre Artículo', 'Id Concepto', 'Nombre Concepto', 'Id Subconcepto', 'Nombre Subconcepto', 'Presupuesto '+field_username, field_username+' Reales'])
    for year in set(c['economic_breakdown'].years.values()):
        write_breakdown_item(writer, year, c['economic_breakdown'], field, [c['article_id'], None, None], c['descriptions'][field])
        for heading_id, heading in c['economic_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, heading, field, [c['article_id'], heading_id, None], c['descriptions'][field])
            for item_uid, item in heading.subtotals.iteritems():
                write_breakdown_item(writer, year, item, field, [c['article_id'], heading_id, item_uid], c['descriptions'][field])

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
    for year in set(c['funding_breakdown'].years.values()):
        for source_id, source in c['funding_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, source, c['show_side'], [source_id, None], c['descriptions']['funding'])
            for fund_id, fund in source.subtotals.iteritems():
                write_breakdown_item(writer, year, fund, c['show_side'], [source_id, fund_id], c['descriptions']['funding'])

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
    writer.writerow(['#Año', 'Nombre Organismo', 'Nombre Departamento', 'Presupuesto '+field_username, field_username+' Reales'])
    for year in set(c['institutional_breakdown'].years.values()):
        for institution_id, institution in c['institutional_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, institution, c['show_side'], [institution_id, None], c['descriptions']['institutional'])
            for department_id, department in institution.subtotals.iteritems():
                write_breakdown_item(writer, year, department, c['show_side'], [institution_id, department_id], c['descriptions']['institutional'])

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
    for year in set(c['economic_breakdown'].years.values()):
        for entity_id, entity in c['economic_breakdown'].subtotals.iteritems():
            write_breakdown_item(writer, year, entity, field, [entity_id])

def write_entities_expenses_breakdown(c, writer):
    return write_entities_breakdown(c, 'expense', writer)

def entities_expenses(request, level, format):
    return entities_index(request, get_context(request), level, _generator('gastos_%ss' % level, format, write_entities_expenses_breakdown))

def write_entities_income_breakdown(c, writer):
    return write_entities_breakdown(c, 'income', writer)

def entities_income(request, level, format):
    return entities_index(request, get_context(request), level, _generator('ingresos_%ss' % level, format, write_entities_income_breakdown))


#
# Helper code to output any CSV/Excel line
#
def write_breakdown_item(writer, year, item, field, ids, descriptions=None):
    budget_column_name = str(year)
    actual_column_name = 'actual_'+str(year)
    totals = item.total_expense if field == 'expense' else item.total_income

    if not totals.get(budget_column_name) and not totals.get(actual_column_name):
        return

    values = [year]

    for id in ids:
        values.append( id.encode("utf-8") if id!=None else id )
        if descriptions!=None:
            values.append( descriptions.get(id, '').encode("utf-8") )

    # The original amounts are in cents:
    values.append( totals[budget_column_name] / 100.0 if budget_column_name in totals else None )
    values.append( totals[actual_column_name] / 100.0 if actual_column_name in totals else None )

    writer.writerow(values)


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
