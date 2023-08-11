import logging

from FlightsApi.facades import AnonymousFacade, AirlineFacade

from rest_framework.views import APIView
from rest_framework.response import Response
from dateutil import parser
from datetime import datetime
from django.utils import timezone

from FlightsApi.utils.response_utils import bad_request_response, forbidden_response
from FlightsApi.utils import StringValidation

logger = logging.getLogger('django')

class FlightsView(APIView): # /flights
    def get(self, request):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Validate and fetch request parameters
        
        origin_country_id = request.GET.get('origin_country')
        if origin_country_id and not StringValidation.is_natural_int(origin_country_id):
            code, data = bad_request_response("Origin country must be a natural number.")
            return Response(status=code, data=data)
            
        destination_country_id = request.GET.get('destination_country')
        if destination_country_id and not StringValidation.is_natural_int(destination_country_id):
            code, data = bad_request_response("Destination country must be a natural number.")
            return Response(status=code, data=data)
        
        airline_id = request.GET.get('airline')
        if airline_id and not StringValidation.is_natural_int(airline_id):
            code, data = bad_request_response("Airline must be a natural number.")
            return Response(status=code, data=data)
        
        date_str = request.GET.get('date')
        if date_str:
            try:
                date = parser.parse(date_str).date()
            except ValueError as e:
                logger.info(e)
                code, data = bad_request_response("'date' must be in the ISO 8601 format.")
                return Response(status=code, data=data)
        else:
            date = None
        
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

        code, data = facade.get_flights_by_parameters(
            origin_country_id=origin_country_id or None,
            destination_country_id=destination_country_id or None,
            date=date,
            airline_id=airline_id or None,
            limit=limit,
            page=page
        )
        return Response(status=code, data=data)
        
    
    def post(self, request):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        # Origin Country Validation
        origin_country_id = request.GET.get('origin_country')
        if not origin_country_id:
            code, data = bad_request_response("Origin country is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_natural_int(origin_country_id):
            code, data = bad_request_response("Origin country must be a natural number.")
            return Response(status=code, data=data)
            
        # Destination Country Validation
        destination_country_id = request.GET.get('destination_country')
        if not destination_country_id:
            code, data = bad_request_response("Destination country is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_natural_int(destination_country_id):
            code, data = bad_request_response("Destination country must be a natural number.")
            return Response(status=code, data=data)
        
        # Airline Validation
        airline_id = request.GET.get('airline')
        if not airline_id:
            code, data = bad_request_response("Airline is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_natural_int(airline_id):
            code, data = bad_request_response("Airline must be a natural number.")
            return Response(status=code, data=data)
        
        # Total Seats Validation
        total_seats = request.data.get('total_seats')
        if not total_seats:
            code, data = bad_request_response("Total seats is required.")
            return Response(status=code, data=data)
        if not StringValidation.is_natural_int(total_seats):
            code, data = bad_request_response("Total seats must be a natural number.")
            return Response(status=code, data=data)
        
        # Departure DateTime Validation
        departure_datetime_str = request.data.get('departure_datetime')
        if not departure_datetime_str:
            code, data = bad_request_response("Departure datetime is required.")
            return Response(status=code, data=data)
        try:
            departure_datetime = parser.parse(departure_datetime_str).date()
        except ValueError as e:
            logger.debug(e)
            code, data = bad_request_response("Departure datetime must be a valid date (formatted in ISO 8601).")
            return Response(status=code, data=data)
        
        if departure_datetime.tzinfo is not None:
            departure_datetime = timezone.make_naive(departure_datetime)
        if not datetime.now(tz=None) < departure_datetime:
            code, data = bad_request_response("departure_datetime must be in the future.")
            return Response(status=code, data=data)

        # Arrival DateTime Validation
        arrival_datetime_str = request.data.get('arrival_datetime')
        if not arrival_datetime_str:
            code, data = bad_request_response("Arrival datetime is required.")
            return Response(status=code, data=data)
        try:
            arrival_datetime = parser.parse(arrival_datetime_str).date()
        except ValueError as e:
            logger.debug(e)
            code, data = bad_request_response("Arrival datetime must be a valid date (formatted in ISO 8601).")
            return Response(status=code, data=data)
        
        if arrival_datetime.tzinfo is not None:
            arrival_datetime = timezone.make_naive(arrival_datetime)
        if not departure_datetime < arrival_datetime:
            code, data = bad_request_response("arrival_datetime must be after departure_datetime.")
            return Response(status=code, data=data)

        code, data = facade.add_flight(
            origin_id=int(origin_country_id),
            destination_id=int(destination_country_id),
            departure_datetime=departure_datetime,
            arrival_datetime=arrival_datetime,
            total_seats=int(total_seats)
        )
        return Response(status=code, data=data)
    
class FlightView(APIView): # /flight/<id>
    def get(self, request, id):
        facade = AnonymousFacade.login(request)
        
        code, data = facade.get_flight_by_id(id)
        return Response(status=code, data=data)
        
    def patch(self, request, id):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        # Check if flight exists
        status, existing_flight = facade.get_flight_by_id(id)[1]
        if not status == 200:
            return Response(status=status, data=existing_flight)

        # Validate and fetch request parameters
        update_fields = {}
        origin_country_id = request.data.get('origin_country')
        if origin_country_id:
            if not StringValidation.is_natural_int(origin_country_id):
                code, data = bad_request_response("Origin country must be a natural number.")
                return Response(status=code, data=data)
            origin_country_id = int(origin_country_id)
        
        destination_country_id = request.data.get('destination_country')
        if destination_country_id:
            if not StringValidation.is_natural_int(destination_country_id):
                code, data = bad_request_response("Destination country must be a natural number.")
                return Response(status=code, data=data)
            destination_country_id = int(destination_country_id)
            
        total_seats = request.data.get('total_seats')
        if total_seats:
            if not StringValidation.is_natural_int(total_seats):
                code, data = bad_request_response("Total seats must be a natural number.")
                return Response(status=code, data=data)
            total_seats = int(total_seats)

        departure_datetime_str = request.data.get('departure_datetime')
        arrival_datetime_str = request.data.get('arrival_datetime')
        
        if departure_datetime_str:
            try:
                departure_datetime = parser.parse(departure_datetime_str)
            except ValueError as e:
                logger.info(e)
                code, data = bad_request_response("Departure date/time is in an invalid format.")
                return Response(status=code, data=data)

            if departure_datetime.tzinfo is not None:
                departure_datetime = timezone.make_naive(departure_datetime)
            if not datetime.now(tz=None) < departure_datetime:
                code, data = bad_request_response("Departure date/time must be in the future.")
                return Response(status=code, data=data)
            if not arrival_datetime_str: 
                # Check if departure datetime is before the current arrival datetime
                temp_arrival_datetime = parser.parse(existing_flight['arrival_datetime'])
                if temp_arrival_datetime.tzinfo is not None:
                    temp_arrival_datetime = timezone.make_naive(temp_arrival_datetime)
                if not departure_datetime < temp_arrival_datetime:
                    code, data = bad_request_response("Departure date/time must be before arrival date/time.")
                    return Response(status=code, data=data)
        else:
            departure_datetime = None
        
        if arrival_datetime_str:
            try:
                arrival_datetime = parser.parse(arrival_datetime_str)
            except ValueError as e:
                logger.info(e)
                code, data = bad_request_response("Arrival date/time is in an invalid format.")
                return Response(status=code, data=data)
            if arrival_datetime.tzinfo is not None:
                arrival_datetime = timezone.make_naive(arrival_datetime)
            if departure_datetime:
                if not departure_datetime < arrival_datetime:
                    code, data = bad_request_response("Arrival date/time must be after departure date/time.")
                    return Response(status=code, data=data)
            else:
                temp_departure_datetime = parser.parse(existing_flight['departure_datetime'])
                if temp_departure_datetime.tzinfo is not None:
                    temp_departure_datetime = timezone.make_naive(temp_departure_datetime)
                
                if not temp_departure_datetime < arrival_datetime:
                    code, data = bad_request_response("Arrival date/time must be after departure date/time.")
                    return Response(status=code, data=data)
        else:
            arrival_datetime = None

        update_fields['origin_country'] = origin_country_id or None
        update_fields['destination_country'] = destination_country_id or None
        update_fields['total_seats'] = total_seats or None
        update_fields['departure_datetime'] = departure_datetime or None
        update_fields['arrival_datetime'] = arrival_datetime or None
        
        code, data = facade.update_flight(id, **update_fields)
        return Response(status=code, data=data)
    
    def delete(self, request, id):
        # Get correct facade
        facade = AnonymousFacade.login(request)
        
        # Check if the user has the right permissions
        if not isinstance(facade, AirlineFacade):
            code, data = forbidden_response()
            return Response(status=code, data=data)
        
        code, data = facade.cancel_flight(id)
        return Response(status=code, data=data)