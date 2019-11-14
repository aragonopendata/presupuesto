from coffin.shortcuts import render_to_response
from budget_app.models import Budget, BudgetBreakdown, BudgetItem, Entity
from helpers import *
from properties import *


def tax_receipt(request):
    c = get_context(request, css_class='body-tax-receipt', title='')

    # Get latest budget data
    populate_latest_budget(c)
    populate_descriptions(c)
    c['default_income'] = 30000

    # Get the budget breakdown
    c['breakdown'] = BudgetBreakdown(['policy', 'programme'])
    for item in BudgetItem.objects.each_denormalized("b.id = %s", [c['latest_budget'].id]):
        c['breakdown'].add_item(c['latest_budget'].name(), item)
        
    c['draftBudgetYear'] = draftBudgetYear
    c['draftBudgetYear_2'] = draftBudgetYear_2

    return render_to_response('tax_receipt/index.html', c)
