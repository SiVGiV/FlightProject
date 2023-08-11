from ..facades import AnonymousFacade, AdministratorFacade

from rest_framework.views import APIView
from rest_framework.response import Response

from FlightsApi.utils.response_utils import bad_request_response, forbidden_response
from FlightsApi.utils import StringValidation

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
        if not username:
            code, data = bad_request_response("Username is required.")
            return Response(status=code, data=data)
        
        password = request.data.get('password')
        if not password:
            code, data = bad_request_response("Password is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_valid_password(password):
            code, data = bad_request_response("Password must be at least 8 characters long and contain at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special character.")
            return Response(status=code, data=data)
                
        email = request.data.get('email')
        if not email:
            code, data = bad_request_response("Email is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_valid_email(email):
            code, data = bad_request_response("Email is invalid.")
            return Response(status=code, data=data)
        
        first_name = request.data.get('first_name')
        if not first_name:
            code, data = bad_request_response("First name is required.")
            return Response(status=code, data=data)
        
        last_name = request.data.get('last_name')
        if not last_name:
            code, data = bad_request_response("Last name is required.")
            return Response(status=code, data=data)
        
        
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