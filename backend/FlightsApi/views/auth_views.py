from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from FlightsApi.utils.response_utils import no_content_ok, forbidden_response
from FlightsApi.facades import AnonymousFacade


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        code, res = no_content_ok()
        return Response(status=code, data=res)

class LoginView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            code, res = no_content_ok()
            return Response(status=code, data=res)
        else:
            code, res = forbidden_response()
            return Response(status=code, data=res)
    
class WhoAmIView(APIView):
    def get(self, request):
        facade = AnonymousFacade.login(request)
        code, res = facade.whoami()
        return Response(status=code, data=res)