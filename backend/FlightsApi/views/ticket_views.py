from FlightsApi.utils.response_utils import bad_request_response, forbidden_response
from FlightsApi.utils import StringValidation
from ..facades import AnonymousFacade, CustomerFacade

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class TicketsView(APIView): # /tickets
    def get(self, request):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, CustomerFacade):
            code, data = forbidden_response('You do not have the right permissions.')
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
        
        code, data = facade.get_my_tickets(limit=limit, page=page)
        return Response(status=code, data=data)
    
    def post(self, request):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, CustomerFacade):
            code, data = forbidden_response('You do not have the right permissions.')
            return Response(status=code, data=data)
        
        flight_id = request.data.get('flight_id')
        seat_count = request.data.get('seat_count')
        # Validate inputs
        if not flight_id:
            code, data = bad_request_response('You must select a flight.')
            return Response(status=code, data=data)
        if not StringValidation.is_natural_int(flight_id):
            code, data = bad_request_response('Flight ID must be a natural number.')
            return Response(status=code, data=data)

        if not seat_count:
            code, data = bad_request_response('You must select an amount of seats to purchase.')
            return Response(status=code, data=data)
        if not StringValidation.is_natural_int(seat_count):
            code, data = bad_request_response('Seat count must be a natural number.')
            return Response(status=code, data=data)
        
        code, data = facade.add_ticket(flight_id=int(flight_id), seat_count=int(seat_count))
        return Response(status=code, data=data)
    
class TicketView(APIView): # /ticket/<id>    
    def delete(self, request, id):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, CustomerFacade):
            code, data = forbidden_response('You do not have the right permissions.')
            return Response(status=code, data=data)
        
        code, data = facade.cancel_ticket(id)
        return Response(status=code, data=data)