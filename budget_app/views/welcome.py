from coffin.shortcuts import render_to_response
from django.conf import settings
from budget_app.models import Budget, Entity, FunctionalCategory, BudgetBreakdown
from helpers import *
from random import sample


def welcome(request):
    c = get_context(request, css_class='body-welcome', title='Inicio')
    c['formatter'] = add_thousands_separator

    # Retrieve front page examples
    populate_latest_budget(c)
    c['featured_programmes'] = list(FunctionalCategory.objects
                                .filter(budget=c['latest_budget'])
                                .filter(programme__in=settings.FEATURED_PROGRAMMES))

    # Get only 3 random items from all Featured Programmes
    if len(c['featured_programmes']) > 3:
        c['featured_programmes'] = sample(c['featured_programmes'], 3)

    # Decide whether we're going to show budget or execution figures
    use_actual = False
    for programme in c['featured_programmes']:
        if (BudgetItem.objects
                    .filter(functional_category=programme)
                    .filter(actual=True).count()) > 0:
            use_actual = True
            break

    # Calculate subtotals for the selected programmes
    c['breakdown'] = BudgetBreakdown(['programme'])
    for programme in c['featured_programmes']:
        for item in programme.budgetitem_set.filter(actual=use_actual):
            c['breakdown'].add_item(c['latest_budget'].year, item)

    return render_to_response('welcome/index.html', c)
