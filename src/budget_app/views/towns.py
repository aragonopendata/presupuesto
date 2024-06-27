# -*- coding: UTF-8 -*-
from counties import counties_show, counties_compare
from entities import entities_index, entities_show, entities_compare, entities_show_article, entities_show_policy
from helpers import *
import json


def towns(request, render_callback=None):
    c = get_context(request, css_class='body-entities', title='Municipios')
    return entities_index(request, c, 'municipio', render_callback)


def towns_show(request, town_slug, render_callback=None):
    town = _get_town(town_slug)
    return entities_show(request, _get_town_context(request, town), town, render_callback)


def towns_show_income(request, town_slug, id, render_callback=None):
    town = _get_town(town_slug)
    c = _get_town_context(request, town)
    return entities_show_article(request, c, town, id, '', 'income', render_callback)


def towns_show_expense(request, town_slug, id, render_callback=None):
    town = _get_town(town_slug)
    c = _get_town_context(request, town)
    return entities_show_article(request, c, town, id, '', 'expense', render_callback)


def towns_show_fexpense(request, town_slug, id, render_callback=None):
    town = _get_town(town_slug)
    c = _get_town_context(request, town)
    return entities_show_policy(request, c, town, id, '', render_callback)


def towns_compare(request, town_left_slug, town_right_slug):
    town_left = _get_town(town_left_slug)
    town_right = _get_town(town_right_slug)
    c = get_context(request, 
                    css_class='body-entities', 
                    title='Comparativa '+town_left.name+'/'+town_right.name+' - Municipios')
    return entities_compare(request, c, town_left, town_right)


# Retrieve the entity to display from the given slug
def _get_town(slug):
    return Entity.objects.get(level='municipio', slug=slug)


# Get request context for a town page
def _get_town_context(request, town):
    c = get_context(request, css_class='body-entities', title=town.name +' - Municipios')
    populate_entities(c, town.level)
    return c
