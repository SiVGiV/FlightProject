from ..facades import AnonymousFacade

from rest_framework.views import APIView
from rest_framework.response import Response

from FlightsApi.utils.response_utils import bad_request_response

class CountriesView(APIView):
    def get(self, request): # /countries
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            code, data = bad_request_response(error_msg)
            return Response(status=code, data=data)
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
            page = int(request.GET.get('page', 1))
        except ValueError:
            code, data = bad_request_response('Pagination limit or page are not integers.')
            return Response(status=code, data=data)
        
        code, data = facade.get_all_countries(limit=limit, page=page)
        return Response(status=code, data=data)
    
class CountryView(APIView):
    def get(self, request, id: int): # /country/<id>
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            code, data = bad_request_response(error_msg)
            return Response(status=code, data=data)
        
        # Create response
        code, data = facade.get_country_by_id(id)
        return Response(status=code, data=data)