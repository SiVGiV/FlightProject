# Python builtin imports
from typing import Tuple
from datetime import datetime
import logging

# Django imports
from django.core.exceptions import ValidationError

# App imports
from FlightsApi.repository import Repository as R, DBTables, Paginate
from FlightsApi.repository import errors as RepoErrors
from FlightsApi.utils.response_utils import not_found_response, bad_request_response, \
                            ok_response, created_response, internal_error_response, \
                            no_content_ok, forbidden_response

# Local module imports
from .facade_base import FacadeBase

logger = logging.getLogger('django')

class AirlineFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('airlinecompany')
        self.__user = user
        self.__user['airline'] = R.get_by_user_id(DBTables.AIRLINECOMPANY, self.__user['id'])
    
    @staticmethod
    def usertype():
        return 'airline'
    
    @property 
    def required_group(self):
        return self.__required_group

    def get_my_flights(self, limit: int = 50, page: int = 0):
        """Get the airline's flights

        Args:
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 0.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        try:
            data = R.get_flights_by_airline_id(self.__user['airline']['id'])
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)

        pagination = Paginate(limit, page)
        return ok_response(data=data, pagination=pagination)

    def update_airline(self, name: str = None, country_id: int = None) -> Tuple[int, dict]:
        """Updates the airline.

        Args:
            name (str, optional): A new name or None if should not be updated. Defaults to None.
            country_id (int, optional): A new country ID or None if should not be updated. Defaults to None.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors dictionary
        """
        updated_fields = {}
        if name:
            updated_fields.update(name=name)
        if country_id:
            updated_fields.update(country_id=country_id)
        
        try:
            data, success = R.update(DBTables.AIRLINECOMPANY, self.__user['airline']['id'], **updated_fields)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        if success:
            return ok_response(data=data)
        else:
            return bad_request_response(errors=data)

    def add_flight(self, origin_id: int, destination_id: int, departure_datetime: datetime, arrival_datetime: datetime, total_seats: int) -> Tuple[int, dict]:
        """Add a new flight to the airline

        Args:
            origin_id (int): Origin country id
            destination_id (int): Destination country id
            departure_datetime (datetime): Departure datetime
            arrival_datetime (datetime): Landing datetime
            total_seats (int): Total seats on the flight

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors dictionary
        """
        try:
            data, success = R.add(
                DBTables.FLIGHT,
                airline=self.__user['airline']['id'],
                origin_country=origin_id,
                destination_country=destination_id,
                departure_datetime=departure_datetime,
                arrival_datetime=arrival_datetime,
                total_seats=total_seats    
            )
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        if not success:
            return bad_request_response(errors=data)

        return created_response(data)

    def update_flight(self, flight_id: int, **updated_fields) -> Tuple[int, dict]:
        """Update a flight owned by the airline

        Args:
            flight_id (int): ID of the flight to edit

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors dictionary
        """
        try:
            flight = R.get_by_id(DBTables.FLIGHT, flight_id)
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not flight:
            return not_found_response(errors=RepoErrors.EntityNotFoundException())
        
        # Make sure this airline owns the flight
        if not flight['airline'] == self.__user['airline']['id']:
            return forbidden_response()

        try:
            updated_flight, success = R.update(DBTables.FLIGHT, id=flight_id, **updated_fields)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)

        if success:
            return ok_response(updated_flight)
        else:
            return bad_request_response(errors=updated_flight)

    def cancel_flight(self, flight_id: int) -> Tuple[int, dict]:
        """Cancels a flight

        Args:
            flight_id (int): The flight's id

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors dictionary
        """
        try:
            flight = R.get_by_id(DBTables.FLIGHT, flight_id)
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
            
        # Check if flight exists
        if not flight:
            return not_found_response(errors=RepoErrors.EntityNotFoundException())
        
        if not flight['airline'] == self.__user['airline']['id']:
            return forbidden_response()
        
        try:
            data, success = R.update(DBTables.FLIGHT, id=flight_id, is_canceled=True)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not data['is_canceled']:
            return internal_error_response()
        return no_content_ok()
        
    def get_airlines_by_name(self, name: str = '',  limit: int = 50, page: int = 1):
        """Overrides FacadeBase's function and removes the user information from it.

        Args:
            name (str, optional): Name to filter by. Defaults to empty string ("")
            limit (int, optional): Maximum results per page. Defaults to 50.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            Tuple[int, dict]: A response tuple contianing status code and data/errors dictionary
        """
        code, data =  super().get_airlines_by_name(name, limit, page)
        if code != 200:
            return code, data
        if 'data' in data:
            for airline in data['data']:
                airline.pop('user', None)
        return code, data
    
    def get_airline_by_id(self, id: int):
        """Overrides FacadeBase's function and removes the user information from it.

        Args:
            id (int): ID to look up.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        code, data =  super().get_airline_by_id(id)
        if code != 200:
            return code, data
        if self.__user['airline']['id'] != id:
            if 'data' in data:
                data['data'].pop('user', None)
        return code, data
