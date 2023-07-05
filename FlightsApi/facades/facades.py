# Local project imports
from ..repository import Repository as R, DBTables, Paginate
from ..repository import errors as RepoErrors
from ..utils import is_customer, is_airline, is_admin
from .errors import *
# Python builtin imports
from datetime import datetime, date as Date
from typing import Tuple
from abc import abstractmethod
# Django imports
from django.contrib.auth import login
from django.http import HttpRequest
from rest_framework import status
from django.core.exceptions import ValidationError

__groups_created = False
DATE_FORMAT = "%Y-%m-%d"

class FacadeBase():    
    @abstractmethod
    def required_group(self):
        """
        A required property getter to be overridden by inheriting classes.
        """
        pass
    
    @staticmethod
    def get_all_flights(limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Fetches all flights (paginated) from the repository

        Args:
            limit (int, optional): Maximum amount of results per call. Defaults to 100.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            Tuple[int, dict]: Status code, data
        """
        # Initialize pagination
        pagination = Paginate(per_page=limit, page_number=page)
        
        # Fetch data
        try:
            data = R.get_all(DBTables.FLIGHT, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Return response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
    
    @staticmethod
    def get_flight_by_id(id: int) -> Tuple[int, dict]:
        """Fetches a flight from the repo by a given ID

        Args:
            id (int): Flight ID

        Returns:
            Tuple[int, dict]: Status code, data
        """
        # Fetch data and handle repository errors
        try:
            data = R.get_by_id(DBTables.FLIGHT, id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors':["'id' must be larger than zero."]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            return status.HTTP_404_NOT_FOUND, {'errors':['The requested resource was not found.']}
        
        # Return response
        return status.HTTP_200_OK, {'data': data}
    
    @staticmethod
    def get_flights_by_parameters(origin_country_id: int = None, destination_country_id: int = None, date: Date = None, limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Get all flights and filter by given parameters.

        Args:
            origin_country_id (int, optional): Id of the flight's origin country. Defaults to None.
            destination_country_id (int, optional): Id of the flight's destination country. Defaults to None.
            date (Date, optional): Date of departure. Defaults to None.
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 1.

        Returns:
            Tuple[int, dict]: Status code, data
        """
        # Initialize pagination
        pagination = Paginate(limit, page)
        
        # Fetch data and handle exceptions
        try:
            data = R.get_flights_by_parameters(origin_country_id, destination_country_id, date, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Return response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
        
    @staticmethod
    def get_all_airlines(limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Get all airlines

        Args:
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 1.

        Returns:
            Tuple[int, dict]: Status code, data
        """
        # Initialize pagination
        pagination = Paginate(limit, page)
        
        # Fetch data and handle exceptions
        try:
            data = R.get_all(DBTables.AIRLINECOMPANY, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
                
        # Return response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
    
    @staticmethod
    def get_airline_by_id(id: int) -> Tuple[int, dict]:
        """Get an airline by a given ID

        Args:
            id (int): An airline ID. Must be greater than 0.

        Returns:
            Tuple[int, dict]: Status code, data
        """
        # Fetch airline and handle exceptions
        try:
            data = R.get_by_id(DBTables.AIRLINECOMPANY, id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ["'id' must be larger than zero."]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            return status.HTTP_404_NOT_FOUND, {'errors': ['The requested resource was not found.']}
        
        # Return response
        return status.HTTP_200_OK, {'data': data}
    
    @staticmethod
    def get_airlines_by_name(name: str, limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Get all airlines whos name contains a certain string.

        Args:
            name (str): String to search in the airlines' names.
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 1.

        Returns:
            Tuple[int, dict]: Status code, data.
        """
        # Initialize pagination
        pagination = Paginate(limit, page)
        
        # Fetch airlines and handle exceptions
        try:
            data = R.get_airlines_by_name(name, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
                
        # Return response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}

    @staticmethod
    def get_all_countries(limit: int = 50, page: int = 0) -> Tuple[int, dict]:
        """Gets all countries

        Args:
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 0.

        Returns:
            Tuple[int, dict]: Status code, data
        """
        # Initialize pagination
        pagination = Paginate(per_page=limit, page_number=page)
        
        # Fetch data and handle exceptions
        try:
            data = R.get_all(DBTables.COUNTRY, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Return response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
    
    @staticmethod
    def get_country_by_id(id: int) -> Tuple[int, dict]:
        """Gets a country with a given ID

        Args:
            id (int): ID of a country

        Returns:
            Tuple[int, dict]: Status code, data.
        """
        # Fetch data and handle exceptions
        try:
            data = R.get_by_id(DBTables.COUNTRY, id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ["Country ID must be larger than zero."]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            return status.HTTP_404_NOT_FOUND, {'errors': ['The requested resource was not found.']}
        
        # Return response
        return status.HTTP_200_OK, {'data': data}
        

class AnonymousFacade(FacadeBase):
    """
    An anonymous user serving class.
    """
    def __init__(self):
        super().__init__()
        self.__required_group = None # Anonymous users do not need to be a part of a group
    
    @property 
    def required_group(self):
        return self.__required_group
    
    @staticmethod
    def facade_from_user(user):
        """Returns a facade from a django user object.

        Args:
            user (django.contrib.auth.models.User): A user object used to determine which facade to retrieve.

        Raises:
            RepositoryTransactionException: If failed to create/get permission groups.

        Returns:
            Union[AdministratorFacade, AirlineFacade, CustomerFacade, AnonymousFacade]: _description_
        """
        # Make sure the groups were created - this should happen once on the first facade fetch.
        if not __groups_created:
            try:
                R.get_or_create_group('admin')
                R.get_or_create_group('airline')
                R.get_or_create_group('customer')
            except Exception as e:
                raise RepositoryTransactionException("Failed to get/create permission group.\n" + str(e))
            else:
                __groups_created = True
        
        # Return the right facade
        if is_admin(user):
            return AdministratorFacade(R.serialize_user(user))
        elif is_airline(user):
            return AirlineFacade(R.serialize_user(user))
        elif is_customer(user):
            return CustomerFacade(R.serialize_user(user))
        else:
            return AnonymousFacade()
        
    @staticmethod
    def login(request: HttpRequest) -> Tuple[FacadeBase, str]:
        """Logs a user in, returns the right facade for that user alongside an error message if there was an error.

        Args:
            request (HttpRequest): An http request to login

        Returns:
            Union[FacadeBase, str]: A tuple of Facade, error-message
        """
        # Get user from request
        user = request.user
        
        if user:
            if user.is_anonymous:
                return AnonymousFacade()
            login(request, user) # Django login function
            facade = AnonymousFacade.facade_from_user(user)
            if facade:
                return facade, '' # Return the right facade and an empty reason.
            else:
                return AnonymousFacade(), 'User not assigned to any groups.'
        else:
            return AnonymousFacade(), 'A user with this combination of user/password does not exist.'
    
    def add_customer(self, username, password, email, first_name, last_name, address, phone_number) -> Tuple[int, dict]:
        """Registers a user with a customer role.

        Args:
            username (str): Customer's username
            password (str): Customer's password
            email (str): Customer's email
            first_name (str): Customer's first name
            last_name (str): Customer's last name
            address (str): Customer's address
            phone_number (str): Customer's phone

        Returns:
            Tuple[int, dict]: A Status code and response tuple
        """
        # Create user
        try:
            user_data, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
        except (ValueError, TypeError, ValidationError) as e:
            return 400, {'errors': ['Error while applying request data.', str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not user_created:
            return status.HTTP_400_BAD_REQUEST, {'errors': user_data}
        
        user_id = user_data['id']
        
        # Add user to customer group
        try:
            R.assign_group_to_user(user_id, group_name='customer')
        except RepoErrors.EntityNotFoundException:
            return status.HTTP_400_BAD_REQUEST, {'errors': [f'User ID {user_id} not found.']}
        except RepoErrors.UserAlreadyInGroupException:
            return status.HTTP_409_CONFLICT, {'errors': [f'User ID {user_id} is already assigned to a role.']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Create customer
        try:
            customer_data, customer_created = R.add(
                DBTables.CUSTOMER,
                first_name=first_name,
                last_name=last_name,
                address=address,
                phone_number=phone_number,
                user_id=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            R.assign_group_to_user(user_id, '') # undo the assignment of a group to the user
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            R.assign_group_to_user(user_id, '') # undo the assignment of a group to the user
            return handle_unexpected_exception(e)
        
        if not customer_created:
            return status.HTTP_400_BAD_REQUEST, {'errors': customer_data}

        # Return response
        return status.HTTP_200_OK, {'data': {'customer': customer_data, 'user': user_data}}

    def get_airlines_by_name(self, name: str = '',  limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Overrides FacadeBase's function and removes the user information from the response.

        Args:
            name (str, optional): Name to filter by. Defaults to empty string ("")
            limit (int, optional): Maximum results per page. Defaults to 50.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            Tuple[int, dict]: status code, response data
        """
        code, data =  super().get_airlines_by_name(name, limit, page)
        # If not success return result
        if code != 200:
            return code, data
        # Take out the user data
        for airline in data['data']:
            airline.pop('user', None)
        # Return censored result
        return code, data

class CustomerFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('customer')
        self.__user = user
        
    @property 
    def required_group(self):
        return self.__required_group
        
    def update_customer(self, **updated_fields):
        """Updates a customer's details (Does not update any user credentials!)

        Args:
            updated_fields (kwargs): New details

        Returns:
            Tuple[int, dict]: A response tuple containing [status code, response data/errors]
        """
        try:
            data, success = R.update(DBTables.CUSTOMER, self.__user['customer'], **updated_fields)
        except RepoErrors.FetchError as e:
            res = status.HTTP_404_NOT_FOUND, {'errors': [f"Could not find a customer with the id '{self.__user['customer']}'"]}
        except (ValueError, TypeError, ValidationError) as e:
            res = status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.', str(e)]}
        except Exception as e:
            res = handle_unexpected_exception(e)
        else:
            if success:
                res = status.HTTP_200_OK, {'data':data}
            else:
                res = status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.', data]}
            
        # Return response
        return res


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
            return status.HTTP_409_CONFLICT, {'errors': [f'Cannot book flight because { reason }.']}
        
        # Create ticket
        try:
            data, success = R.add(DBTables.TICKET, flight_id=flight_id, customer_id=self.__user['customer'], seat_count=seat_count)
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        

        if success:
            return status.HTTP_200_OK, {'data': data}
        else:
            return status.HTTP_400_BAD_REQUEST, {'errors': data}


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
            return status.HTTP_400_BAD_REQUEST, {'errors': [str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
            
        # Check if ticket exists
        if not ticket:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Ticket not found.']}
        
        #  Check if this customer owns the ticket
        if not ticket['customer'] == self.__user['customer']:
            return status.HTTP_403_FORBIDDEN, {'errors': ['You cannot modify this ticket since it belongs to a different customer.']}
        
        try:
            data, success = R.update(DBTables.TICKET, id=ticket_id, is_canceled=True)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Ticket not found.']}
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        
        if not success:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ['Something went wrong when cancelling this ticket.', data]}
        return status.HTTP_200_OK, {'data': data}
            

    def get_my_tickets(self, limit: int = 50, page: int = 0) -> Tuple[int, dict]:
        """Gets the customer's tickets

        Args:
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 0.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        paginator = Paginate(limit, page)

        try:
            data = R.get_tickets_by_customer(self.__user['customer'], paginator)
        except Exception as e:
            return handle_unexpected_exception(e)
        return status.HTTP_200_OK, {'data': data, 'pagination': {**paginator}}
    
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
        data['data'].pop('user', None)
        return code, data

class AirlineFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('airlinecompany')
        self.__user = user
    
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
            data = R.get_flights_by_airline_id(self.__user['airline'])
        except Exception as e:
            return handle_unexpected_exception(e)

        pagination = Paginate(limit, page)
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}

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
            data, success = R.update(DBTables.AIRLINECOMPANY, self.__user['airline'], **updated_fields)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Airline not found.']}
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.', str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        

        return status.HTTP_200_OK, {'data': data}

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
                airline_id=self.__user['airline'],
                origin_country_id=origin_id,
                destination_country_id=destination_id,
                departure_datetime=departure_datetime,
                arrival_datetime=arrival_datetime,
                total_seats=total_seats    
            )
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        if not success:
            return status.HTTP_400_BAD_REQUEST, {'errors': data}

        return status.HTTP_200_OK, {'data': data}

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
            return status.HTTP_400_BAD_REQUEST, {'errors': ["Flight ID must be greater than 0."]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not flight:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find flight with ID {flight_id}']}
        
        # Make sure this airline owns the flight
        if not flight['airline'] == self.__user['airline']:
            return status.HTTP_403_FORBIDDEN, {'errors': ['You do not own this flight and cannot update it.']}

        try:
            updated_flight, success = R.update(DBTables.FLIGHT, id=flight_id, **updated_fields)
        except RepoErrors.FetchError as e:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find flight with ID {flight_id}']}
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)

        if success:
            return status.HTTP_200_OK, {'data': updated_flight}
        else:
            return status.HTTP_400_BAD_REQUEST, {'errors': updated_flight}

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
            return status.HTTP_400_BAD_REQUEST, {'errors': [str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
            
        # Check if flight exists
        if not flight:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Flight not found.']}
        
        if not flight['airline'] == self.__user['airline']:
            return status.HTTP_403_FORBIDDEN, {'errors': ['You cannot modify this flight since it belongs to a different airline.']}
        
        try:
            data, success = R.update(DBTables.FLIGHT, id=flight_id, is_canceled=True)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Flight not found.']}
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data['is_canceled']:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ['Something went wrong when cancelling this flight.', str(data)]}
        return status.HTTP_200_OK, {'data': data}
        
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
        data['data'].pop('user', None)
        return code, data

class AdministratorFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('admin')
        self.__user = user

    @property 
    def required_group(self):
        return self.__required_group
    
    def get_all_customers(self, limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Gets all customers in the system

        Args:
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 1.

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        # Retrieve Data
        pagination = Paginate(per_page=limit, page_number=page)
        try:
            data = R.get_all(DBTables.CUSTOMER, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
        
        
    def add_airline(self, username, password, email, name: str, country_id: int) -> Tuple[int, dict]:
        """Creates a user and airline

        Args:
            username (str): The airline's username
            password (str): The airline's password
            email (str): The airline's email
            name (str): The airline's name
            country_id (int): The airline's country ID

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors.
        """
        
        # Create user
        try:
            user, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not user_created:
            return status.HTTP_400_BAD_REQUEST, {'errors': user}
        
        user_id = user['id']
        
        # Add user to airline group
        try:
            R.assign_group_to_user(user_id, group_name='airline')
        except RepoErrors.EntityNotFoundException:
            return status.HTTP_400_BAD_REQUEST, {'errors': [f'User ID {user_id} not found.']}
        except RepoErrors.UserAlreadyInGroupException:
            return status.HTTP_409_CONFLICT, {'errors': [f'User ID {user_id} is already assigned to a role.']}
        except Exception as e:
            return handle_unexpected_exception(e)
                
        # Verify country
        country_exists = R.instance_exists(DBTables.COUNTRY, country_id)
        if not country_exists:
            return status.HTTP_400_BAD_REQUEST, {'errors':[f'Country ID {country_id} not found.']}
        
        # Create airline
        try:
            airline, success = R.add(
                DBTables.AIRLINECOMPANY,
                name=name,
                country_id=country_id,
                user_id=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return handle_unexpected_exception(e)
        
        if success:
            return status.HTTP_200_OK, {'data': {'airline': airline, 'user': user}}
        else:
            return status.HTTP_400_BAD_REQUEST, {'errors': airline}
        
    
    
    def add_customer(self, username: str, password: str, email: str, first_name: str, last_name: str, address: str, phone_number: str) -> Tuple[int, dict]:
        """Create a new customer and user.

        Args:
            username (str): Customer's username
            password (str): Customer's password
            email (str): Customer's email
            first_name (str): Customer's first name
            last_name (str): Customer's last name
            address (str): Customer's address
            phone_number (str): Customer's phone number

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors dictionary.
        """
        # Create user
        try:
            user, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not user_created:
            return status.HTTP_400_BAD_REQUEST, {'errors': user}
        
        user_id = user['id']
        
        # Add user to customer group
        try:
            R.assign_group_to_user(user_id, group_name='customer')
        except RepoErrors.EntityNotFoundException:
            return status.HTTP_400_BAD_REQUEST, {'errors': [f'User ID {user_id} not found.']}
        except RepoErrors.UserAlreadyInGroupException:
            return status.HTTP_409_CONFLICT, {'errors': [f'User ID {user_id} is already assigned to a role.']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Create customer
        try:
            customer, customer_created = R.add(
                DBTables.CUSTOMER,
                first_name=first_name,
                last_name=last_name,
                address=address,
                phone_number=phone_number,
                user_id=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return handle_unexpected_exception(e)
        
        if not customer_created:
            return status.HTTP_400_BAD_REQUEST, {'errors': customer}
        
        return status.HTTP_200_OK, {'data': {'customer': customer, 'user': user}}
    
    
    def add_administrator(self, username: str, password: str, email: str, first_name: str, last_name: str) -> Tuple[int, dict]:
        """Create an administrator and user

        Args:
            username (str): Admin's username
            password (str): Admin's password
            email (str): Admin's email
            first_name (str): Admin's first name
            last_name (str): Admin's last name

        Returns:
            Tuple[int, dict]: A response tuple containing status code and data/errors dictionary.
        """
        # Create user
        try:
            user, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not user_created:
            return status.HTTP_400_BAD_REQUEST, {'errors': user}
        
        user_id = user['id']
        
        # Add user to admin group
        try:
            R.assign_group_to_user(user_id, group_name='admin')
        except RepoErrors.EntityNotFoundException:
            return status.HTTP_400_BAD_REQUEST, {'errors': [f'User ID {user_id} not found.']}
        except RepoErrors.UserAlreadyInGroupException:
            return status.HTTP_409_CONFLICT, {'errors': [f'User ID {user_id} is already assigned to a role.']}
        except Exception as e:
            return handle_unexpected_exception(e)
        # Create admin
        try:
            admin, success = R.add(
                DBTables.ADMIN,
                first_name=first_name,
                last_name=last_name,
                user_id=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.', str(e)]}
        except Exception as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return handle_unexpected_exception(e)
        
        if not success:
            return status.HTTP_400_BAD_REQUEST, {'errors': admin}
        

        return status.HTTP_200_OK, {'data': {'admin': admin, 'user': user}}
    
    def deactivate_airline(self, airline_id: int) -> Tuple[int, dict]:
        """Deactivates an airline account

        Args:
            airline_id (int): An airline ID

        Returns:
            Tuple[int, dict]: A status code and data/errors dictionary
        """
        try:
            airline = R.get_by_id(DBTables.AIRLINECOMPANY, airline_id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Airline ID must be greater than 0.']}
        
        if not airline:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find an airline with the ID {airline_id}']}

        try:
            updated, success = R.update(DBTables.USER, airline['user'], is_active=False)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a user matching an airline with the ID {airline_id}']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if updated['is_active'] == False:
            return status.HTTP_200_OK, {'data': {'success': True}} 
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ['Unexpected failure occured.']}
    
    def deactivate_customer(self, customer_id) -> Tuple[int, dict]:
        """Deactivates a customer account

        Args:
            customer_id (int): A customer ID

        Returns:
            Tuple[int, dict]: A status code and data/errors dictionary
        """
        try:
            customer = R.get_by_id(DBTables.CUSTOMER, customer_id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Customer ID must be greater than 0.']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not customer:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a customer with the ID {customer_id}']}

        try:
            updated, success = R.update(DBTables.USER, customer['user'], is_active=False)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a user matching a customer with the ID {customer_id}']}
        except Exception as e:
            return handle_unexpected_exception(e)

        if updated['is_active'] == False:
            return status.HTTP_200_OK, {'data': {'success': True}}
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ['Unexpected failure occured.']}
        
    
    def deactivate_administrator(self, admin_id) -> Tuple[int, dict]:
        """Deactivates an admin account

        Args:
            admin_id (int): An admin ID

        Returns:
            Tuple[int, dict]: A status code and data/errors dictionary
        """
        try:
            admin = R.get_by_id(DBTables.ADMIN, admin_id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Admin ID must be greater than 0.']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not admin:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find an admin with the ID {admin_id}']}

        try:
            updated, success = R.update(DBTables.USER, admin['user'], is_active=False)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a user matching an admin with the ID {admin_id}']}
        except Exception as e:
            return handle_unexpected_exception(e)
        

        if updated['is_active'] == False:
            return status.HTTP_200_OK, {'data': {'success': True}}
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ['Unexpected failure occured.']}
    

def handle_unexpected_exception(exception) -> Tuple[int, dict]:
    """Creates a status 500 message for an exception.

    Args:
        exception (Exception): Any exception

    Returns:
        Tuple[int, dict]: A 500 status code and an errors dictionary.
    """
    return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ["The server encountered an unexpected error.", str(exception)]}