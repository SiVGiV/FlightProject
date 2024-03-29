import logging

from ..facades import AnonymousFacade, CustomerFacade, AdministratorFacade

from rest_framework.views import APIView
from rest_framework.response import Response

from FlightsApi.utils.response_utils import forbidden_response, bad_request_response
from FlightsApi.utils import StringValidation

logger = logging.getLogger('django')

class CustomersView(APIView): # /customers
    def get(self, request):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)

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
        
        code, data = facade.get_all_customers(limit=limit, page=page)
        return Response(status=code, data=data)
        
    
    def post(self, request):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, (AdministratorFacade, AnonymousFacade)):
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
        
        first_name = request.data.get('first_name')
        if not first_name:
            code, data = bad_request_response("First name is required.")
            return Response(status=code, data=data)
        
        last_name = request.data.get('last_name')
        if not last_name:
            code, data = bad_request_response("Last name is required.")
            return Response(status=code, data=data)
        
        address = request.data.get('address')
        if not address:
            code, data = bad_request_response("Address is required.")
            return Response(status=code, data=data)        
        
        phone_number = request.data.get('phone_number')
        if not phone_number:
            code, data = bad_request_response("Phone number is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_valid_phone_number(phone_number):
            code, data = bad_request_response("Enter a valid Israeli phone number.")
            return Response(status=code, data=data)
                
        code, data = facade.add_customer(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            address=address,
            phone_number=phone_number
        )
        return Response(status=code, data=data)
    
class CustomerView(APIView): # /customer/<id>
    def get(self, request, id):
        """
        GET /customer/<id> - Deactivate customer account
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, (CustomerFacade, AdministratorFacade)):
            code, data = forbidden_response()
        
        # Call facade and return response
        else:
            code, data = facade.get_customer_by_id(id)
            
        return Response(status=code, data=data)
    
    def delete(self, request, id):
        """
        DELETE /customer/<id> - Deactivate customer account
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            code, data = forbidden_response()       
        
        # Call facade and return response
        else:
            code, data = facade.deactivate_customer(id)
            
        return Response(status=code, data=data)
        
    def patch(self, request, id):
        """
        PATCH /customer/<id> - Update a customer
        """
        # Get correct facade
        facade = AnonymousFacade.login(request)

        # Check if the user has the right permissions
        if not isinstance(facade, CustomerFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)

        update_fields = {}

        first_name = request.data.get('first_name')
        if first_name:
            update_fields['first_name'] = first_name
            
        last_name = request.data.get('last_name')
        if last_name:
            update_fields['last_name'] = last_name
            
        address = request.data.get('address')
        if address:
            update_fields['address'] = address
            
        phone_number = request.data.get('phone_number')
        if phone_number:
            if not StringValidation.is_valid_phone_number(phone_number):
                code, data = bad_request_response("Enter a valid Israeli phone number.")
                return Response(status=code, data=data)
            update_fields['phone_number'] = phone_number
        code, data = facade.update_customer(id, **update_fields)
        return Response(status=code, data=data)
