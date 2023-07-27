from django.contrib.auth import logout
from rest_framework.decorators import api_view
from rest_framework.response import Response
from FlightsApi.utils.response_utils import no_content_ok, forbidden_response
from FlightsApi.facades import AnonymousFacade

@api_view(['POST'])
def logout(request):
    logout(request)
    code, res = no_content_ok()
    return Response(status=code, data=res)

@api_view(['POST'])
def login(request):
    if request.user.is_authenticated:
        code, res = no_content_ok()
        return Response(status=code, data=res)
    else:
        code, res = forbidden_response()
        return Response(status=code, data=res)
    
@api_view(['GET'])
def whoami(request):
    facade = AnonymousFacade.login(request)
    code, res = facade.whoami()
    return Response(status=code, data=res)