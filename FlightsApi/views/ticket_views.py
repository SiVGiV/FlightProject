from ..facades import AnonymousFacade, CustomerFacade, AirlineFacade, AdministratorFacade

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class TicketsView(APIView): # /tickets
    def get(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, CustomerFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
            page = int(request.GET.get('page', 1))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Pagination limit or page are not integers.']})
        
        
        code, data = facade.get_my_tickets(limit=limit or 50, page=page or 1)
        return Response(status=code, data=data)
    
    def post(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, CustomerFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Validate inputs
        try:
            flight_id = int(request.data.get('flight_id'))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'flight_id' must be an integer."]})
        
        try:
            seat_count = int(request.data.get('seat_count'))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'seat_count' must be an integer."]})
        
        code, data = facade.add_ticket(flight_id=flight_id, seat_count=seat_count)
        return Response(status=code, data=data)
    
class TicketView(APIView): # /ticket/<id>    
    def delete(self, request, id):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, CustomerFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        code, data = facade.cancel_ticket(id)
        return Response(status=code, data=data)