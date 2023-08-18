import logging

from ..facades import AnonymousFacade, AirlineFacade, AdministratorFacade

from rest_framework.views import APIView
from rest_framework.response import Response

from FlightsApi.utils.response_utils import forbidden_response, bad_request_response
from FlightsApi.utils import StringValidation

logger = logging.getLogger('django')


class AirlinesView(APIView): # /airlines
    def get(self, request):
        """
        GET /airlines - Get all airlines / filter by name
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Get all the details
        name = request.GET.get('name', '')
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
        except TypeError:
            code, data = bad_request_response('Pagination limit is not a valid integer.')
            return Response(status=code, data=data)
        try:
            page = int(request.GET.get('page', 1))
        except TypeError:
            code, data = bad_request_response('Pagination page is not a valid integer.')
            return Response(status=code, data=data)
        
        # Call facade and return response
        code, data = facade.get_airlines_by_name(
            name=name,
            limit=limit,
            page=page
        )
        return Response(status=code, data=data)
    
    def post(self, request):
        """
        POST /airlines - Add a new airline
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)

        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
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
                
        name = request.data.get('name')
        if not name:
            code, data = bad_request_response("Name is required.")
            return Response(status=code, data=data)
        
        country_id = request.data.get('country')
        if not country_id:
            code, data = bad_request_response("Country is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_natural_int(country_id):
            code, data = bad_request_response("Country must be a natural integer.")
            return Response(status=code, data=data)
        country_id = int(country_id)
        
        code, data = facade.add_airline(
            username=username,
            password=password,
            email=email,
            name=name,
            country_id=country_id
        )
        return Response(status=code, data=data)
    
    
    
class AirlineView(APIView): # /airline/<id>
    def get(self, request, id):
        """
        GET /airline/<id> - Get airline by id
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Call facade and return response
        code, data = facade.get_airline_by_id(id)
        return Response(status=code, data=data)
    
    def delete(self, request, id):
        """
        DELETE /airline/<id> - Deactivate airline account
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        # Call facade and return response
        code, data = facade.deactivate_airline(id)
        return Response(status=code, data=data)
    
    def patch(self, request, id):
        """
        PATCH /airline/<id> - Update an airline
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        update_fields = {}
        name = request.data.get('name', '')
        if name:
            update_fields['name'] = name
            
        country_id = request.data.get('country', '')
        if country_id:
            if not StringValidation.is_natural_int(country_id):
                code, data = bad_request_response('Country ID must be a natural integer.')
                return Response(status=code, data=data)
            country_id = int(country_id)
            update_fields['country'] = country_id

        code, data = facade.update_airline(**update_fields)
        return Response(status=code, data=data)