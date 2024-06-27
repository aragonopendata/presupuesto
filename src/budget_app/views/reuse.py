from coffin.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from helpers import *


def reuse(request):
    c = get_context(request, css_class='body-reuse', title=_('Inicio'))
    return render_to_response('reuse/index.html', c)
