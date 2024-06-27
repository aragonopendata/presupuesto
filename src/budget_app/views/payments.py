# -*- coding: UTF-8 -*-
from coffin.shortcuts import render_to_response
from budget_app.models import BudgetBreakdown, Payment
from helpers import *

def payments(request, render_callback=None):
    # Get request context
    c = get_context(request, css_class='body-payments', title='Inversiones y pagos')

    # Payments breakdown
    c['payee_breakdown'] = BudgetBreakdown(['payee', 'area', 'description'])
    c['area_breakdown'] = BudgetBreakdown(['area', 'payee', 'description'])

    for item in Payment.objects.each_denormalized():
        # We add the date to the description, if it exists:
        # TODO: I wanted the date to be in a separate column, but it's complicated right
        # now the way BudgetBreakdown works. Need to think about it
        if item.date:
            item.description = item.description + ' (' + str(item.date) + ')'

        c['payee_breakdown'].add_item(item.year, item)
        c['area_breakdown'].add_item(item.year, item)

    # Additional data needed by the view
    populate_stats(c)
    populate_years(c, 'area_breakdown')

    return render_to_response('payments/index.html', c)
