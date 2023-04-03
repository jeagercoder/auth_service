from django.shortcuts import HttpResponse
from django.conf import settings


class InternalServiceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get('HTTP_PROXY_AUTHORIZATION')
        if auth is None :
            return HttpResponse('Forbidden', status=403)
        auth = auth.split(' ')
        if len(auth) != 2:
            return HttpResponse('Forbidden', status=403)
        if auth[0] != settings.INTERNAL_AUTH_PREFIX or auth[1] != settings.INTERNAL_AUTH_VALUE:
            return HttpResponse('Forbidden', status=403)
        response = self.get_response(request)
        return response
