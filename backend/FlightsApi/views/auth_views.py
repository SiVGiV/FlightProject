from django.contrib.auth import logout
from rest_framework.response import Response
from FlightsApi.utils.response_utils import no_content_ok, forbidden_response
from facades import AnonymousFacade

def logout(request):
    logout(request)
    request.COOKIES['usertype'] = 'anon'
    code, res = no_content_ok()
    return Response(status=code, data=res)

def login(request):
    if request.user.is_authenticated:
        code, res = no_content_ok()
        return Response(status=code, data=res)
    else:
        code, res = forbidden_response()
        return Response(status=code, data=res)
    
def whoami(request):
    facade = AnonymousFacade.login(request)
    code, res = facade.whoami()
    return Response(status=code, data=res)