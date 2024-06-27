from coffin.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage
from django.conf import settings
from budget_app.models import Budget, Payment, GlossaryTerm, FunctionalCategory, BudgetItem, Entity
from helpers import *


def search(request):
    c = get_context(request, css_class='body-search', title='')

    c['query'] = request.GET.get('q', '')
    populate_latest_budget(c)
    c['selected_year'] = str(request.GET.get('year', c['latest_budget'].year))
    c['page'] = request.GET.get('page', 1)
    c['query_string'] = "year=%s&q=%s&" % (c['selected_year'], c['query'])

    # If no parameter is given we show results for the latest budget. In order
    # to search across all budgets one needs to request that explicitly.
    if c['selected_year'] != "all":
        year = c['selected_year']
        budgets = Budget.objects.filter(entity__id=get_main_entity(c).id, year=year)
        budget = budgets[0] if len(budgets)>0 else None
    else:
        year = None
        budget = None

    # Get search results
    c['years'] = map(str, Budget.objects.get_years())
    c['terms'] = list(GlossaryTerm.objects.search(c['query']))
    if not hasattr(settings, 'SEARCH_ENTITIES') or settings.SEARCH_ENTITIES:
        c['entities'] = list(Entity.objects.search(c['query']))
        c['show_entity_names'] = True

    all_items = list(BudgetItem.objects.search(c['query'], year, c['page']))
    try:
        c['items'] = Paginator(all_items, 10).page(c['page'])
    except EmptyPage:
        pass

    all_payments = list(Payment.objects.search(c['query'], year))
    try:
        c['payments'] = Paginator(all_payments, 10).page(c['page'])
    except EmptyPage:
        pass

    # Consolidate policies and programmes search results, to avoid duplicates
    # XXX: We're searching only in top-level entity, the other ones are spotty,
    # not sure it's worth the effort; plus the search results UX is complicated.
    policies = list(FunctionalCategory.objects.search_policies(c['query'], budget))
    programmes = list(FunctionalCategory.objects.search_programmes(c['query'], budget))
    c['policies_ids'] = list(set([policy.uid() for policy in policies]))
    c['programmes_per_policy'] = {}
    for programme in programmes:
        if not c['programmes_per_policy'].get(programme.policy, None):
            c['programmes_per_policy'][programme.policy] = set()
        c['programmes_per_policy'][programme.policy].add(programme.programme)

    c['results_size'] = len(c['terms']) + len(c['policies_ids']) + len(all_items) + len(all_payments)
    c['formatter'] = add_thousands_separator
    c['main_entity_level'] = settings.MAIN_ENTITY_LEVEL

    # XXX: Note we only have top-level descriptions. Beware on the view not to use
    # the wrong descriptions. We should fetch the descriptions from the DB together with
    # the results if needed.
    populate_descriptions(c)

    # Count the size of the programme sets
    for programmes in c['programmes_per_policy'].values():
        c['results_size'] += len(programmes)

    return render_to_response('search/index.html', c)
