# -*- coding: UTF-8 -*-
from coffin.shortcuts import render_to_response
from aragon.models import BudgetBreakdown, Entity, EconomicCategory
from helpers import *

def entities_index(request, c, level, render_callback=None):
    # Get the budget breakdown
    c['economic_breakdown'] = BudgetBreakdown(['name'])
    # The top level entity has a nicely broken down budget, where each item is classified across
    # 4 dimensions. For smaller entities, however, we have two separate breakdowns as input,
    # that are loaded separately, with dummy values ('X') assigned to the three unknown dimensions. 
    # To avoid double counting, we must calculate breakdowns along a dimension including only
    # those items for which we know the category (i.e. not 'X')
    get_budget_breakdown(   "e.level = %s and ec.chapter <> 'X'", [ level ], 
                            [ 
                                c['economic_breakdown'] 
                            ])

    # Additional data needed by the view
    populate_level(c, level)
    populate_level_stats(c, level)
    populate_years(c, 'economic_breakdown', level)
    populate_entities(c, level)

    # XXX: The percentage format in pages listing entities is tricky and confusing, partly because
    # we have many gaps in the data which vary each year, so I'm hiding the drop-down option for now.
    c['hide_percentage_format'] = True
    
    return render(c, render_callback, 'entities/index.html')


def entities_show(request, c, entity, render_callback=None):
    # Prepare the budget breakdowns
    c['financial_expense_breakdown'] = BudgetBreakdown()
    c['functional_breakdown'] = BudgetBreakdown(['policy', 'programme'])
    if entity.level == 'comunidad':
        c['economic_breakdown'] = BudgetBreakdown(['article', 'heading'])
    else:
        # Small entities have a varying level of detail: often we don't have any breakdown below
        # chapter, so we have to start there. Also, to be honest, the heading level doesn't add
        # much to what you get with articles.
        c['economic_breakdown'] = BudgetBreakdown(['chapter', 'article'])

    get_budget_breakdown(   "e.id = %s and fc.area <> 'X'", [ entity.id ],
                            [],
                            get_financial_breakdown_callback(c) )
    get_budget_breakdown(   "e.id = %s and ec.chapter <> 'X'", [ entity.id ],
                            [ c['economic_breakdown'] ] )

    # Additional data needed by the view
    populate_level(c, entity.level)
    populate_entity_stats(c, entity)
    populate_entity_descriptions(c, entity)
    populate_years(c, 'economic_breakdown', entity.level)
    populate_area_descriptions(c, ['functional', 'income', 'expense'])
    c['display_functional_view'] = True
    _set_full_breakdown(c, entity.level == 'comunidad')
    c['entity'] = entity

    return render(c, render_callback, 'entities/show.html')


def entities_compare(request, c, entity_left, entity_right):
    c['entity_left'] = entity_left
    c['entity_right'] = entity_right

    # Get the budget breakdowns
    # XXX: No good functional data at this level so far
    # c['functional_breakdown_left'] = BudgetBreakdown(['policy'])
    c['economic_breakdown_left'] = BudgetBreakdown(['chapter', 'article'])
    get_budget_breakdown(   "e.name = %s and ec.chapter <> 'X'", [ entity_left.name ],
                            [ 
                                c['economic_breakdown_left'] 
                            ])

    c['economic_breakdown_right'] = BudgetBreakdown(['chapter', 'article'])
    get_budget_breakdown(   "e.name = %s and ec.chapter <> 'X'", [ entity_right.name ],
                            [ 
                                c['economic_breakdown_right'] 
                            ])

    # Additional data needed by the view
    populate_level(c, entity_left.level)
    populate_entity_stats(c, entity_left, 'stats_left')
    populate_entity_stats(c, entity_right, 'stats_right')
    populate_entity_descriptions(c, entity_left)
    populate_area_descriptions(c, ['income', 'expense'])
    populate_comparison_years(c, 'economic_breakdown_left', 'economic_breakdown_right')
    populate_entities(c, entity_left.level)

    return render_to_response('entities/compare.html', c)


def entities_show_policy(request, c, entity, id, title, render_callback=None):
    # Get request context
    c = get_context(request, css_class='body-policies', title='')
    c['policy_uid'] = id

    # Get the budget breakdown
    c['functional_breakdown'] = BudgetBreakdown(['function', 'programme'])
    c['economic_breakdown'] = BudgetBreakdown(['chapter', 'article', 'heading'])
    c['funding_breakdown'] = BudgetBreakdown(['source', 'fund'])
    c['institutional_breakdown'] = BudgetBreakdown([_year_tagged_section, _year_tagged_department])
    get_budget_breakdown(   "fc.policy = %s and e.id = %s", [ id, entity.id ],
                            [ 
                                c['functional_breakdown'], 
                                c['economic_breakdown']
                            ])

    # Additional data needed by the view
    show_side = 'expense'
    populate_level(c, entity.level)
    populate_entity_stats(c, entity)
    populate_entity_descriptions(c, entity)
    populate_years(c, 'functional_breakdown', entity.level)
    populate_area_descriptions(c, ['functional', show_side])
    _populate_csv_settings(c, 'policy', id)
    _set_show_side(c, show_side)
    _set_full_breakdown(c, False)
    c['entity'] = entity

    c['name'] = c['descriptions']['functional'].get(c['policy_uid'])
    c['title_prefix'] = c['name']

    return render(c, render_callback, 'policies/show.html')


# Prepare all data needed for an article breakdown page (i.e. economic dimension)
# XXX: As a workaround for the really spotty data we've got for small entities, this
# function can now also handle 'chapters'. This is needed because sometimes (no-XBRL data)
# that's the only data we have.
def entities_show_article(request, c, entity, id, title, show_side, render_callback=None):
    # Get request context
    c = get_context(request, css_class='body-policies', title='')
    c['article_id'] = id
    c['is_chapter'] = len(id) <= 1
    if c['is_chapter']:
        c['article'] = EconomicCategory.objects.filter( budget__entity=entity,
                                                        chapter=id, 
                                                        expense=(show_side=='expense'))[0]
    else:
        c['article'] = EconomicCategory.objects.filter( budget__entity=entity,
                                                        article=id, 
                                                        expense=(show_side=='expense'))[0]

    # Ignore if possible the descriptions for execution data, they are truncated and ugly
    article_descriptions = {}
    def _populate_article_descriptions(column_name, item):
        if not item.actual or not item.uid() in article_descriptions:
            article_descriptions[item.uid()] = getattr(item, 'description')

    # Get the budget breakdown.
    # The functional breakdown is an empty one because our small entity data is not fully broken, 
    # down but since we're going to be displaying this data in the policy page we send a blank one
    c['functional_breakdown'] = BudgetBreakdown([])
    if c['is_chapter']:
        # XXX: Some entities combine different levels of data detail along the years. Trying
        # to display detailed categories (articles, headings) looks bad on the visualization,
        # because some years just 'disappear'. So we take the 'safe route', just visualizing
        # the chapter total.
        c['economic_breakdown'] = BudgetBreakdown(['chapter', 'article'])
        query = "ec.chapter = %s and e.id = %s"
    else:
        c['economic_breakdown'] = BudgetBreakdown(['heading', 'uid'])
        query = "ec.article = %s and e.id = %s"
    c['funding_breakdown'] = BudgetBreakdown(['source', 'fund'])
    c['institutional_breakdown'] = BudgetBreakdown([_year_tagged_section, _year_tagged_department])
    get_budget_breakdown(   query, [ id, entity.id ],
                            [ 
                                c['economic_breakdown'],
                                c['funding_breakdown'],
                                c['institutional_breakdown']
                            ],
                            _populate_article_descriptions)

    # Note we don't modify the original descriptions, we're working on a copy (of the hash,
    # which is made of references to the hashes containing the descriptions themselves).
    c['descriptions'] = Budget.objects.get_all_descriptions(entity).copy()
    article_descriptions.update(c['descriptions'][show_side])
    c['descriptions'][show_side] = article_descriptions
    c['name'] = c['descriptions'][show_side].get(c['article_id'])
    c['title_prefix'] = c['name'] + ' - ' + entity.name

    # Additional data needed by the view
    populate_level(c, entity.level)
    populate_entity_stats(c, entity)
    populate_years(c, 'institutional_breakdown', entity.level)
    populate_area_descriptions(c, ['functional', 'funding', show_side])
    _populate_csv_settings(c, 'article', id)
    _set_show_side(c, show_side)
    _set_full_breakdown(c, False)
    c['entity'] = entity

    return render(c, render_callback, 'policies/show.html')


# Unfortunately institutions id change sometimes over the years, so we need to
# use id's that are unique along time, not only inside a given budget.
def _year_tagged_section(item):
    section = getattr(item, 'section') if getattr(item, 'section') else ''
    return str(getattr(item, 'year')) + '/' + section


def _year_tagged_department(item):
    department = getattr(item, 'department') if getattr(item, 'department') else ''
    return str(getattr(item, 'year')) + '/' + department


def _get_tab_titles(show_side):
    if show_side == 'income':
        return {
            'economic': u"¿Cómo se ingresa?",
            'funding': u"Tipo de ingresos",
            'institutional': u"¿Quién recauda?"
        }
    else:
        return {
            'functional': u"¿En qué se gasta?",
            'economic': u"¿Cómo se gasta?",
            'funding': u"¿Cómo se financia?",
            'institutional': u"¿Quién lo gasta?"
        }

def _populate_csv_settings(c, type, id):
    c['csv_id'] = id
    c['csv_type'] = type

def _set_show_side(c, side):
    c['show_side'] = side
    c['tab_titles'] = _get_tab_titles(side)

# Do we have an exhaustive budget, classified along four dimensions? I.e. display all tabs?
def _set_full_breakdown(c, full_breakdown):
    c['full_breakdown'] = full_breakdown
