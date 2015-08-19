from django.middleware.cache import UpdateCacheMiddleware, FetchFromCacheMiddleware
from django.conf import settings
from discount.models import request_with_empty_guest


#def cache_required(request):



class DiscountUpdateCacheMiddleware(UpdateCacheMiddleware):
    def _should_update_cache(self, request, response):
        if not settings.DISCOUNT_CACHE_ENABLED:
            return False
        if request_with_empty_guest(request):
            return super()._should_update_cache(request, response)
        else:
            return False



class DiscountFetchFromCacheMiddleware(FetchFromCacheMiddleware):
    def process_request(self, request):
        if not settings.DISCOUNT_CACHE_ENABLED:
            request._cache_update_cache = False
            return None
        if request_with_empty_guest(request):
            return super().process_request(request)
        else:
            request._cache_update_cache = False
            return None


class DiscountAuthenticationMiddleware:
    def process_request(self, request):
        #request.session.save()
        assert hasattr(request, 'user'), (
            "AuthenticationMiddleware hasn't been invoked"
        )
        #loc.user = request.user



