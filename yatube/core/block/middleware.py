from django.http import HttpResponseForbidden


class BlockPythonRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if 'python-requests' in user_agent:
            return HttpResponseForbidden('Access denied')
        return self.get_response(request)


class BlockIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_ips = []

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR', '')
        if ip_address in self.blocked_ips:
            return HttpResponseForbidden('Access denied')
        return self.get_response(request)
