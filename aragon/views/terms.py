from coffin.shortcuts import render_to_response
from django.core.paginator import Paginator
from aragon.models import GlossaryTerm
from helpers import *


def terms(request):
    c = get_context(request, css_class='body-glossary', title='Inicio')

    c['query'] = request.GET.get('q', '')
    c['query_string'] = "q=%s&" % (c['query'])
    page = request.GET.get('page', 1)

    results = Paginator(list(GlossaryTerm.objects.search(c['query'])), 10)
    c['terms'] = results.page(page)

    return render_to_response('terms/index.html', c)
