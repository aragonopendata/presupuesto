# -*- coding: UTF-8 -*-
from coffin.shortcuts import render_to_response
from budget_app.models import BudgetBreakdown, Entity
from entities import entities_index, entities_show, entities_compare, entities_show_article, entities_show_policy
from helpers import *


def counties(request, render_callback=None):
    c = get_context(request, css_class='body-counties', title='Comarcas')
    return entities_index(request, c, 'comarca', render_callback)


def counties_show(request, county_slug, render_callback=None):
    county = _get_county(county_slug)
    return entities_show(request, _get_county_context(request, county), county, render_callback)


def counties_show_income(request, county_slug, id, render_callback=None):
    county = _get_county(county_slug)
    c = _get_county_context(request, county)
    return entities_show_article(request, c, county, id, '', 'income', render_callback)


def counties_show_expense(request, county_slug, id, render_callback=None):
    county = _get_county(county_slug)
    c = _get_county_context(request, county)
    return entities_show_article(request, c, county, id, '', 'expense', render_callback)


def counties_show_fexpense(request, county_slug, id, render_callback=None):
    county = _get_county(county_slug)
    c = _get_county_context(request, county)
    return entities_show_policy(request, c, county, id, '', render_callback)


def counties_compare(request, county_left_slug, county_right_slug):
    county_left = _get_county(county_left_slug)
    county_right = _get_county(county_right_slug)
    c = get_context(request, 
                    css_class='body-counties', 
                    title='Comparativa '+county_left.name+'/'+county_right.name+' - Comarcas')
    return entities_compare(request, c, county_left, county_right)


# Retrieve the entity to display from the given slug
def _get_county(slug):
    return Entity.objects.get(level='comarca', slug=slug)


# Get request context for a county page
def _get_county_context(request, county):
    c = get_context(request, css_class='body-entities', title=county.name +' - Comarcas')
    populate_entities(c, county.level)
    return c
