from django.middleware.cache import UpdateCacheMiddleware

import re

# We need to remove Google Analytics cookies or they'll break the cache
# as soon as there's a "Vary: Cookie" header, which is our case.
# See https://github.com/aragonopendata/presupuesto/issues/12 for more info.
class SmartUpdateCacheMiddleware(UpdateCacheMiddleware):
    STRIP_RE = re.compile(r'\b(_[^=]+=.+?(?:; |$))')

    def process_request(self, request):
        cookie = self.STRIP_RE.sub('', request.META.get('HTTP_COOKIE', ''))
        request.META['HTTP_COOKIE'] = cookie
