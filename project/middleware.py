from django.middleware.cache import UpdateCacheMiddleware

import re

class SmartUpdateCacheMiddleware(UpdateCacheMiddleware):
    STRIP_RE = re.compile(r'\b(_[^=]+=.+?(?:; |$))')

    def process_request(self, request):
        cookie = self.STRIP_RE.sub('', request.META.get('HTTP_COOKIE', ''))
        request.META['HTTP_COOKIE'] = cookie
