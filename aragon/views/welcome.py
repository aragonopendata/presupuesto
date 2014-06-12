from coffin.shortcuts import render_to_response
from aragon.models import Budget, Entity, FunctionalCategory, BudgetBreakdown
from helpers import *


def welcome(request):
    c = get_context(request, css_class='body-welcome', title='Inicio')
    c['formatter'] = add_thousands_separator

    # Retrieve front page examples
    populate_latest_budget(c)
    c['featured_programmes'] = (FunctionalCategory.objects
                                .filter(budget=c['latest_budget'])
                                .filter(programme__in=['24121', '24221', '35131']))

    # Calculate subtotals for the selected programmes
    c['breakdown'] = BudgetBreakdown(['programme'])
    for programme in c['featured_programmes']:
        for item in programme.budgetitem_set.all():
            c['breakdown'].add_item(c['latest_budget'].year, item)

    return render_to_response('welcome/index.html', c)
