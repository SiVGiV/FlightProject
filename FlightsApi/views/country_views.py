from ..facades import AnonymousFacade, CustomerFacade, AirlineFacade, AdministratorFacade

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class CountriesView(APIView):
    def get(self, request): # /countries
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
            page = int(request.GET.get('page', 1))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Pagination limit or page are not integers.']})
        
        code, data = facade.get_all_countries(limit=limit, page=page)
        return Response(status=code, data=data)
    
class CountryView(APIView):
    def get(self, request, id: int): # /country/<id>
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        # Create response
        code, data = facade.get_country_by_id(id)
        return Response(status=code, data=data)