# Python builtin imports
from typing import Tuple
import logging

# Django imports
from django.core.exceptions import ValidationError

# App imports
from FlightsApi.repository import Repository as R, DBTables, Paginate
from FlightsApi.repository import errors as RepoErrors
from FlightsApi.utils.response_utils import conflict_response, not_found_response, bad_request_response, \
                            ok_response, created_response, internal_error_response, \
                            forbidden_response

# Local module imports
from .facade_base import FacadeBase

logger = logging.getLogger('django')

class CustomerFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('customer')
        self.__user = user
        self.__user['customer'] = R.get_by_user_id(DBTables.CUSTOMER, self.__user['id'])
        
    @property
    def usertype(self):
        return 'customer'
        
    @property
    def required_group(self):
        return self.__required_group
    
    @property
    def username(self):
        return self.__user['username']
    
    @property
    def id(self):
        return self.__user['id']
    
    @property
    def entity_id(self):
        return self.__user['customer']['id']

    @property
    def entity_name(self):
        return self.__user['customer']['first_name'] + " " + self.__user['customer']['last_name']

    def get_customer_by_id(self, id: int):
        """Get a customer's details
        
        Args:
            id (int): Customer's ID

        Returns:
            Tuple[int, dict]: A response tuple containing [status code, response data/errors]
        """
        if not int(self.entity_id) == id:
            return forbidden_response()
        
        try:
            data = R.get_by_id(DBTables.CUSTOMER, id)
        except (RepoErrors.FetchError, RepoErrors.EntityNotFoundException) as e:
            logger.error(e)
            return not_found_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        else:
            if data:
                return ok_response(data) 
            else:
                return not_found_response()

    def update_customer(self, id, **updated_fields):
        """Updates a customer's details (Does not update any user credentials!)

        Args:
            id (int): Customer ID (used for verification)
            updated_fields (kwargs): New details

        Returns:
            Tuple[int, dict]: A response tuple containing [status code, response data/errors]
        """
        if not int(self.entity_id) == id:
            return forbidden_response()
        
        try:
            data, success = R.update(DBTables.CUSTOMER, int(self.entity_id), **updated_fields)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            return bad_request_response(errors=e) 
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        else:
            if success:
                return ok_response(data)
            else:
                return bad_request_response(errors=data)


    def add_ticket(self, flight_id: int, seat_count: int) -> Tuple[int, dict]:
        """Adds a flight ticket for a customer

        Args:
            flight_id (int): ID of the flight
            seat_count (int): # of seats for this ticket

        Returns:
            Tuple[int, dict]: A response tuple containing status code and response/error details.
        """
        # Check if possible
        bookable, reason = R.is_flight_bookable(flight_id, seat_count)
        if not bookable:
            return conflict_response(errors=f'Cannot book flight because { reason }.')
        
        # Create ticket
        try:
            data, success = R.add(DBTables.TICKET, flight=flight_id, customer=int(self.entity_id), seat_count=seat_count)
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e) 
            return internal_error_response(errors=e)
        

        if success:
            return created_response(data)
        else:
            if 'non_field_errors' in data:
                if data['non_field_errors'][0].code == 'unique':
                    return conflict_response(errors=["Customer already has a ticket for this flight.", "duplicate_ticket"])
            return bad_request_response(errors=data)


    def cancel_ticket(self, ticket_id: int) -> Tuple[int, dict]:
        """Cancels a ticket

        Args:
            ticket_id (int): A ticket's ID

        Returns:
            Tuple[int, dict]: A response tuple containing status code, data/error dictionary
        """
        try:
            ticket = R.get_by_id(DBTables.TICKET, ticket_id)
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
            
        # Check if ticket exists
        if not ticket:
            return not_found_response(errors=RepoErrors.EntityNotFoundException())
        
        #  Check if this customer owns the ticket
        if not ticket['customer'] == int(self.entity_id):
            return forbidden_response()
        
        try:
            data, success = R.update(DBTables.TICKET, id=ticket_id, is_cancelled=True)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            return bad_request_response(errors=e)
        
        if not success:
            return internal_error_response('Failed to update ticket.')
        return ok_response(data=data)
            

    def get_my_tickets(self, limit: int = 50, page: int = 0) -> Tuple[int, dict]:
        """Gets the customer's tickets

        Args:
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 0.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        pagination = Paginate(limit, page)

        try:
            data = R.get_tickets_by_customer(int(self.entity_id), pagination)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        return ok_response(data=data, pagination=pagination)
    
    def get_airlines_by_name(self, name: str = '',  limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Overrides FacadeBase's function and censors the user information from it.

        Args:
            name (str, optional): Name to filter by. Defaults to empty string ("")
            limit (int, optional): Maximum results per page. Defaults to 50.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        code, data =  super().get_airlines_by_name(name, limit, page)
        # If not success return result
        if code != 200:
            return code, data
        # Take out the user data
        if 'data' in data:
            for airline in data['data']:
                airline.pop('user', None)
        # Return censored result
        return code, data
    
    def get_airline_by_id(self, id: int):
        """Overrides FacadeBase's function and censors the user information from it.

        Args:
            id (int): ID to look up.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        code, data =  super().get_airline_by_id(id)
        if code != 200:
            return code, data
        if 'data' in data:
            data['data'].pop('user', None)
        return code, data
    
    
    def get_flights_by_parameters(self, *args, **kwargs):
        return super().get_flights_by_parameters(*args, **kwargs, allow_cancelled = False)