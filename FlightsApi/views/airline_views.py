from ..facades import AnonymousFacade, CustomerFacade, AirlineFacade, AdministratorFacade

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

class AirlinesView(APIView): # /airlines
    def get(self, request):
        """
        GET /airlines - Get all airlines / filter by name
        """
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Get all the details
        name = request.GET.get('name', '')
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
            page = int(request.GET.get('page', 1))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Pagination limit or page are not integers.']})
        
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
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        name = request.POST.get('name')
        try:
            country_id = int(request.POST.get('country'))
        except TypeError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'country' must be an integer."]})
        
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
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Call facade and return response
        code, data = facade.get_airline_by_id(id)
        return Response(status=code, data=data)
    
    def delete(self, request, id):
        """
        DELETE /airline/<id> - Deactivate airline account
        """
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AdministratorFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Call facade and return response
        code, data = facade.deactivate_airline(id)
        return Response(status=code, data=data)
    
    def patch(self, request, id):
        """
        PATCH /airline/<id> - Update an airline
        """
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        update_fields = {}
        name = request.PATCH.get('name', '')
        if name:
            update_fields['name'] = name
        try:
            country_id = int(request.PATCH.get('country', ''))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Country ID must be an integer.']})
        if country_id:
            update_fields['country'] = country_id

        code, data = facade.update_airline(**update_fields)
        return Response(status=code, data=data)