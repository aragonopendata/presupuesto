from coffin.shortcuts import render_to_response
from django.core.paginator import Paginator
from django.utils.translation import ugettext as _
from budget_app.models import GlossaryTerm
from helpers import *


def terms(request):
    c = get_context(request, css_class='body-glossary', title=_('Inicio'))

    c['query'] = request.GET.get('q', '')
    c['query_string'] = "q=%s&" % (c['query'])
    page = request.GET.get('page', 1)

    results = Paginator(list(GlossaryTerm.objects.search(c['query'])), 10)
    c['terms'] = results.page(page)

    return render_to_response('terms/index.html', c)
