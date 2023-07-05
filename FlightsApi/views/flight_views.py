from ..facades import AnonymousFacade, CustomerFacade, AirlineFacade, AdministratorFacade

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class FlightsView(APIView): # /flights
    def get(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Validate and fetch request parameters
        try:
            origin_country_id = int(request.GET.get('origin_country', 0))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'origin_country' must be an integer."]})
        
        try:
            destination_country_id = int(request.GET.get('destination_country', 0))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'destination_country' must be an integer."]})
        
        date = request.GET.get('date', None)
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
            page = int(request.GET.get('page', 1))
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ['Pagination limit or page are not integers.']})
                
        code, data = facade.get_flights_by_parameters(
            origin_country_id=origin_country_id or None,
            destination_country_id=destination_country_id or None,
            date=date or None,
            limit=limit or 50,
            page=page or 1
        )
        return Response(status=code, data=data)
        
    
    def post(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Validate and fetch request parameters
        try:
            origin_country_id = int(request.POST.get('origin_country', 0))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'origin_country' must be an integer."]})
        
        try:
            destination_country_id = int(request.POST.get('destination_country', 0))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'destination_country' must be an integer."]})
        
        try:
            total_seats = int(request.POST.get('total_seats', 0))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'total_seats' must be an integer."]})
        
        departure_datetime = request.POST.get('departure_datetime', None)
        arrival_datetime = request.POST.get('arrival_datetime', None)
        
        code, data = facade.add_flight(
            origin_id=origin_country_id or None,
            destination_id=destination_country_id or None,
            departure_datetime=departure_datetime or None,
            arrival_datetime=arrival_datetime or None,
            total_seats=total_seats or None
        )
        return Response(status=code, data=data)
    
class FlightView(APIView): # /flight/<id>
    def get(self, request, id):
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        code, data = facade.get_flight_by_id(id)
        return Response(status=code, data=data)
        
    def patch(self, request, id):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        # Validate and fetch request parameters
        update_fields = {}
        try:
            origin_country_id = int(request.POST.get('origin_country', 0))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'origin_country' must be an integer."]})
        if origin_country_id:
            update_fields['origin_country'] = origin_country_id
            
        try:
            destination_country_id = int(request.POST.get('destination_country', 0))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'destination_country' must be an integer."]})
        if destination_country_id:
            update_fields['destination_country'] = destination_country_id
        
        try:
            total_seats = int(request.POST.get('total_seats', 0))
        except TypeError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': ["'total_seats' must be an integer."]})
        if total_seats:
            update_fields['total_seats'] = total_seats
        
        departure_datetime = request.POST.get('departure_datetime', None)
        if departure_datetime:
            update_fields['departure_datetime'] = departure_datetime
            
        arrival_datetime = request.POST.get('arrival_datetime', None)
        if arrival_datetime:
            update_fields['arrival_datetime'] = arrival_datetime
        
        code, data = facade.update_flight(id, **update_fields)
        return Response(status=code, data=data)
    
    def delete(self, request, id):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'errors': [error_msg]})
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            return Response(status=status.HTTP_403_FORBIDDEN, data={'errors': ['You do not have the right permissions.']})
        
        code, data = facade.cancel_flight(id)
        return Response(status=code, data=data)