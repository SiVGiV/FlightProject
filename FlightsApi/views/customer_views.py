from ..facades import AnonymousFacade, CustomerFacade, AirlineFacade, AdministratorFacade

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

class CustomersView(APIView): # /customers
    def get(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
            page = int(request.GET.get('page', 1))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Pagination limit or page are not integers.']})
        
        code, data = facade.get_all_customers(request, limit=limit or 0, page=page or 0)
        return Response(status=code, data=data)
        
    
    def post(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, (AdministratorFacade, AnonymousFacade)):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        
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
    def delete(self, request, id):
        """
        DELETE /customer/<id> - Deactivate customer account
        """
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Call facade and return response
        code, data = facade.deactivate_customer(id)
        return Response(status=code, data=data)
        
    
@api_view(['PATCH'])
def update_customer_view(request):
    """
    PATCH /customer/<id> - Update a customer
    """
    # Get correct facade
    facade, error_msg = AnonymousFacade.login(request)
    if error_msg:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
    
    # Check if the user has the right permissions
    if not isinstance(facade, CustomerFacade):
        return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
    
    update_fields = {}
    
    first_name = request.POST.get('first_name')
    if first_name:
        update_fields['first_name'] = first_name
    last_name = request.POST.get('last_name')
    if last_name:
        update_fields['last_name'] = last_name
    address = request.POST.get('address')
    if address:
        update_fields['address'] = address
    phone_number = request.POST.get('phone_number')
    if phone_number:
        update_fields['phone_number'] = phone_number

    code, data = facade.update_customer(**update_fields)
    return Response(status=code, data=data)