from django.contrib.auth import logout, login, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from FlightsApi.utils.response_utils import no_content_ok, forbidden_response, bad_request_response
from FlightsApi.facades import AnonymousFacade, AdministratorFacade


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        code, res = no_content_ok()
        return Response(status=code, data=res)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            code, res = bad_request_response('username and password are required')
            return Response(status=code, data=res)
        user = authenticate(username=username, password=password)
        if not user:
            code, res = bad_request_response("This combination of username and password does not exist.")
            return Response(status=code, data=res)
        login(request, user)
        code, res = no_content_ok()
        return Response(status=code, data=res)

class WhoAmIView(APIView):
    def get(self, request):
        facade = AnonymousFacade.login(request)
        code, res = facade.whoami()
        return Response(status=code, data=res)

class CSRFTokenView(APIView):
    @method_decorator(csrf_exempt)
    def get(self, request):
        csrf_token = get_token(request)
        return Response(status=200, data={'data': {'CSRF-Token': csrf_token}})
    
    
class UsersView(APIView):
    def get(self, request, usertype):
        facade = AnonymousFacade.login(request)
        if not isinstance(facade, AdministratorFacade):
            code, res = forbidden_response()
            return Response(status=code, data=res)
        
        code, res = facade.get_users_by_usertype(usertype)
        return Response(status=code, data=res)