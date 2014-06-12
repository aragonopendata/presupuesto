from coffin.shortcuts import render_to_response
from aragon.models import Budget, BudgetBreakdown, BudgetItem
from helpers import *


def budgets(request):
    c = get_context(request, css_class='body-counties', title='')

    # Income/expense breakdown
    c['functional_breakdown'] = BudgetBreakdown(['policy', 'programme'])
    c['economic_breakdown'] = BudgetBreakdown(['article', 'heading'])
    for item in BudgetItem.objects.each_denormalized("e.level = %s", ['comunidad']):
        column_name = year_column_name(item)
        if not item.is_financial():
            c['functional_breakdown'].add_item(column_name, item)
            c['economic_breakdown'].add_item(column_name, item)

    # Additional data needed by the view
    populate_stats(c)
    populate_descriptions(c)
    populate_years(c, 'functional_breakdown')

    return render_to_response('budgets/index.html', c)
