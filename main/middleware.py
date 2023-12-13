from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect


URL_REDIRECT = '/accounts/login/'


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated and \
           not request.path == URL_REDIRECT:
            return HttpResponseRedirect(URL_REDIRECT + '?next=' + request.path)
        return None
