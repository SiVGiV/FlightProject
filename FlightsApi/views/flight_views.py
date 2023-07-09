from FlightsApi.facades import AnonymousFacade, AirlineFacade

from rest_framework.views import APIView
from rest_framework.response import Response
from dateutil import parser

from FlightsApi.utils.response_utils import bad_request_response, forbidden_response


class FlightsView(APIView): # /flights
    def get(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            code, data = bad_request_response(error_msg)
            return Response(status=code, data=data)
        
        # Validate and fetch request parameters
        try:
            origin_country_id = int(request.GET.get('origin_country', 0)) or None
        except ValueError:
            code, data = bad_request_response("'origin_country' must be an integer.")
            return Response(status=code, data=data)
        
        try:
            destination_country_id = int(request.GET.get('destination_country', 0)) or None
        except ValueError:
            code, data = bad_request_response("'destination_country' must be an integer.")
            return Response(status=code, data=data)
        
        try:
            date_str = request.GET.get('date', '')
            if date_str:
                date = parser.parse(date_str).date()
            else:
                date = None
        except ValueError as e:
            code, data = bad_request_response("'date' must be in the ISO 8601 format.")
            return Response(status=code, data=data)
        
        # Validate pagination inputs
        try:
            limit = int(request.GET.get('limit', 50))
            page = int(request.GET.get('page', 1))
        except ValueError:
            code, data = bad_request_response('Pagination limit and page must be integers.')
            return Response(status=code, data=data)
                
        code, data = facade.get_flights_by_parameters(
            origin_country_id=origin_country_id or None,
            destination_country_id=destination_country_id or None,
            date=date,
            limit=limit,
            page=page
        )
        return Response(status=code, data=data)
        
    
    def post(self, request):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            code, data = bad_request_response(error_msg)
            return Response(status=code, data=data)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        # Validate and fetch request parameters
        try:
            origin_country_id = int(request.data.get('origin_country', 0))
        except TypeError:
            code, data = bad_request_response("'origin_country' must be an integer.")
            return Response(status=code, data=data)
        
        try:
            destination_country_id = int(request.data.get('destination_country', 0))
        except TypeError:
            code, data = bad_request_response("'destination_country' must be an integer.")
            return Response(status=code, data=data)
        
        try:
            total_seats = int(request.data.get('total_seats', 0))
        except TypeError:
            code, data = bad_request_response("'total_seats' must be an integer.")
            return Response(status=code, data=data)
        
        
        try:
            departure_datetime_str = request.data['departure_datetime']
            arrival_datetime_str = request.data['arrival_datetime']
            departure_datetime = parser.parse(departure_datetime_str)
            arrival_datetime = parser.parse(arrival_datetime_str)
        except ValueError as e:
            code, data = bad_request_response("'date' must be in the ISO 8601 format.")
            return Response(status=code, data=data)
        except KeyError as e:
            code, data = bad_request_response("request must contain both departure and landing date/time.")
            return Response(status=code, data=data)
        
        code, data = facade.add_flight(
            origin_id=origin_country_id,
            destination_id=destination_country_id,
            departure_datetime=departure_datetime,
            arrival_datetime=arrival_datetime,
            total_seats=total_seats
        )
        return Response(status=code, data=data)
    
class FlightView(APIView): # /flight/<id>
    def get(self, request, id):
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            code, data = bad_request_response(error_msg)
            return Response(status=code, data=data)
        
        code, data = facade.get_flight_by_id(id)
        return Response(status=code, data=data)
        
    def patch(self, request, id):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            code, data = bad_request_response(error_msg)
            return Response(status=code, data=data)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        # Validate and fetch request parameters
        update_fields = {}
        try:
            origin_country_id = int(request.data.get('origin_country', 0))
        except TypeError:
            code, data = bad_request_response("'origin_country' must be an integer.")
            return Response(status=code, data=data)
        
        try:
            destination_country_id = int(request.data.get('destination_country', 0))
        except TypeError:
            code, data = bad_request_response("'destination_country' must be an integer.")
            return Response(status=code, data=data)
        
        try:
            total_seats = int(request.data.get('total_seats', 0))
        except TypeError:
            code, data = bad_request_response("'total_seats' must be an integer.")
            return Response(status=code, data=data)

        try:
            departure_datetime_str = request.data.get('departure_datetime')
            arrival_datetime_str = request.data.get('arrival_datetime')
            departure_datetime = parser.parse(departure_datetime_str)
            arrival_datetime = parser.parse(arrival_datetime_str)
        except ValueError as e:
            code, data = bad_request_response("'date' must be in the ISO 8601 format.")
            return Response(status=code, data=data)
        except KeyError as e:
            code, data = bad_request_response("request must contain both departure and landing date/time.")
            return Response(status=code, data=data)
        
        if origin_country_id:
            update_fields['origin_country'] = origin_country_id
        if destination_country_id:
            update_fields['destination_country'] = destination_country_id
        if total_seats:
            update_fields['total_seats'] = total_seats
        if departure_datetime:
            update_fields['departure_datetime'] = departure_datetime
        if arrival_datetime:
            update_fields['arrival_datetime'] = arrival_datetime
        
        code, data = facade.update_flight(id, **update_fields)
        return Response(status=code, data=data)
    
    def delete(self, request, id):
        # Get correct facade
        facade, error_msg = AnonymousFacade.login(request)
        if error_msg:
            code, data = bad_request_response(error_msg)
            return Response(status=code, data=data)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        code, data = facade.cancel_flight(id)
        return Response(status=code, data=data)