from ..facades import AnonymousFacade, AdministratorFacade

from rest_framework.views import APIView
from rest_framework.response import Response

from FlightsApi.utils.response_utils import bad_request_response, forbidden_response

class AdminsView(APIView): # /admins
    def post(self, request):
        """
        POST /admins - Add a new administrator
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        # Get all the details
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        
        # Call facade and return response
        code, data = facade.add_administrator(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        return Response(status=code, data=data)
    
class AdminView(APIView): # /admin/<id>
    def delete(self, request, id: int):
        """
        DELETE /admin/<int:id> - Deactivate an administrator
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        # Call facade and return response
        code, data = facade.deactivate_administrator(id)
        return Response(status=code, data=data)