# -*- coding: UTF-8 -*-
# Small utility functions shared by all views
from coffin.shortcuts import render_to_response
from budget_app.models import Budget, BudgetItem, InflationStat, PopulationStat, Entity
from django.template import RequestContext
from django.conf import settings
import json

#
# FILLING REQUEST CONTEXT
#

def get_context(request, css_class='', title=''):
    c = RequestContext(request)
    c['page_css_class'] = css_class
    c['title_prefix'] = title

    # Global settings
    c['show_institutional_tab'] = not hasattr(settings, 'SHOW_INSTITUTIONAL_TAB') or settings.SHOW_INSTITUTIONAL_TAB
    c['show_funding_tab'] = hasattr(settings, 'SHOW_FUNDING_TAB') and settings.SHOW_FUNDING_TAB
    c['show_actual'] = not hasattr(settings, 'SHOW_ACTUAL') or settings.SHOW_ACTUAL

    c['color_scale'] = getattr(settings, 'COLOR_SCALE', [])

    return c

def set_title(c, title):
    c['title_prefix'] = title

# This assumes there is only one of the MAIN_ENTITY_LEVEL, which is good enough for now
def get_main_entity(c):
    return Entity.objects.filter(level=settings.MAIN_ENTITY_LEVEL)[0]

def populate_stats(c):  # Convenience: assume it's top level entity
    populate_entity_stats(c, get_main_entity(c))
    
def populate_entity_stats(c, entity, stats_name='stats'):
    c[stats_name] = json.dumps({
        'inflation': InflationStat.objects.get_table(),
        'population': PopulationStat.objects.get_entity_table(entity)
    })
    c['last_inflation_year'] = InflationStat.objects.get_last_year()

def populate_level_stats(c, level):
    c['stats'] = json.dumps({
        'inflation': InflationStat.objects.get_table(),
        'population': PopulationStat.objects.get_level_table(level)
    })
    c['last_inflation_year'] = InflationStat.objects.get_last_year()

# Assumes we're dealing with the top-level entity here
# TODO: Don't like this method, should get rid of it
def populate_descriptions(c):
    c['descriptions'] = Budget.objects.get_all_descriptions(get_main_entity(c))

def populate_entity_descriptions(c, entity):
    c['descriptions'] = Budget.objects.get_all_descriptions(entity)

def populate_years(c, breakdown_name):
    years = sorted(list(set(c[breakdown_name].years.values())))
    c['years'] = json.dumps([str(year) for year in years])
    c['latest_year'] = years[-1]
    c['show_treemap'] = ( len(years) == 1 )

    # Tweak the slider labels when a budget is not final, just proposed
    if _is_proposed_budget():
        years[len(years)-1] = str(years[len(years)-1]) + ' (proyecto)'
    c['years_scale'] = json.dumps([str(year) for year in years])

def populate_comparison_years(c, breakdown_name_left, breakdown_name_right):
    years = sorted(list(set(c[breakdown_name_left].years.values() + c[breakdown_name_right].years.values())))
    c['years'] = json.dumps([str(year) for year in years])
    c['latest_year'] = years[-1]

def populate_budget_statuses(c, entity_id):
    c['budget_statuses'] = json.dumps(Budget.objects.get_statuses(entity_id))

def populate_latest_budget(c):
    c['latest_budget'] = Budget.objects.latest(get_main_entity(c).id)
    return c['latest_budget']

def populate_level(c, level):
    c['level'] = level
    c['is_county'] = (level=='comarca')
    c['show_entity_url'] = 'budget_app.views.counties_show' if (level=='comarca') else 'budget_app.views.towns_show'

def populate_entities(c, level):
    c['entities'] = Entity.objects.entities(level)
    c['entities_json'] = json.dumps(Entity.objects.get_entities_table(level))

def _is_proposed_budget():
    # XXX: Temporary workaround, should come from data model somehow
    return False;


#
# FORMATTING
#
# TODO: Is there a core Django/Python replacement for this?
# TODO: We shouldn't hardcode the thousand separator symbol, should depend on locale
def add_thousands_separator(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + '.'.join(reversed(groups))


#
# TOP AREA DESCRIPTIONS
#

# Retrieve the descriptions for the top level categories, used by visualizations, in JSON
def _get_area_descriptions(descriptions, category):
    areas = {}
    for i in range(10):  # 0..9
        areas[str(i)] = descriptions[category].get(str(i))
    return json.dumps(areas)

# Top level categories descriptions, for visualizations
def populate_area_descriptions(c, areas):
    for area in areas:
        c[area+'_areas'] = _get_area_descriptions(c['descriptions'], area)


#
# BUDGET BREAKDOWNS
#

# Get the breakdown column name given a year and actual/budget
def year_column_name(item):
    if item.actual:
        return 'actual_' + str(getattr(item, 'year'))
    else:
        return str(getattr(item, 'year'))

# Iterate over a set of budget items and calculate a series of breakdowns
def get_budget_breakdown(condition, condition_arguments, breakdowns, callback=None):
    for item in BudgetItem.objects.each_denormalized(condition, condition_arguments):
        column_name = year_column_name(item)
        for breakdown in breakdowns:
            breakdown.add_item(column_name, item)
        if callback:
            callback(column_name, item)

# Auxiliary callback to distinguish financial and non-financial spending
def get_financial_breakdown_callback(c):
    def callback(column_name, item):
        if not c['include_financial_chapters'] and item.is_financial() and item.expense:
            c['financial_expense_breakdown'].add_item(column_name, item)
        else:
            c['functional_breakdown'].add_item(column_name, item)
    return callback


#
# RENDER RESPONSE
#
def render(c, render_callback, template_name):
    if not render_callback:
        return render_to_response(template_name, c)
    else:
        return render_callback.generate_response(c)
