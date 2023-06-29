from ..repository import Repository as R, DBTables, Paginate
from ..repository import errors as RepoErrors
from ..utils import log_action, is_customer, is_airline, is_admin
from datetime import datetime, date as Date
from typing import Union
from abc import abstractmethod
from django.contrib.auth import login
from .errors import *
from rest_framework import status

from django.core.exceptions import ValidationError

from logging import getLogger

logger = getLogger(__name__)
DATE_FORMAT = "%Y-%m-%d"

class FacadeBase():
    
    @abstractmethod
    def required_group(self):
        pass
    
    def get_all_flights(self, limit: int = 100, page: int = 1):
        # Retrieve Data and Handle Errors
        pagination = Paginate(per_page=limit, page_number=page)
        try:
            data = R.get_all(DBTables.FLIGHT, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
    
    
    def get_flight_by_id(self, id: int):
        # Retrieve Data and Handle Errors
        try:
            data = R.get_by_id(DBTables.FLIGHT, id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors':["'id' must be larger than zero."]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            return status.HTTP_404_NOT_FOUND, {'errors':['The requested resource was not found.']}
        
        # Make response
        return status.HTTP_200_OK, {'data': data}
    
    
    def get_flights_by_parameters(self, origin_country_id: Union[int, None], destination_country_id: Union[int, None], date: Union[Date, None], limit: int = 100, page: int = 1):
        """_summary_

        Args:
            request (_type_): _description_
            origin_country_id (int): _description_
            destination_country_id (int): _description_
            date (str): A date string in format 'YYYY-MM-DD'
        """
        pagination = Paginate(limit, page)
        
        try:
            data = R.get_flights_by_parameters(origin_country_id, destination_country_id, date, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
        
    def get_all_airlines(self,  limit: int = 100, page: int = 1):
        # Make response
        return FacadeBase.get_airlines_by_name(self, name='', limit=limit, page=page)
    
    
    def get_airline_by_id(self, id: int):
        # Retrieve Data and Handle Errors
        try:
            data = R.get_by_id(DBTables.AIRLINECOMPANY, id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ["'id' must be larger than zero."]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            return status.HTTP_404_NOT_FOUND, {'errors': ['The requested resource was not found.']}
        
        # Make response
        return status.HTTP_200_OK, {'data': data}
    
    def get_airlines_by_name(self, name: str, limit: int = 100, page: int = 1):
        # Retrieve Data and Handle Errors
        pagination = Paginate(limit, page)
        try:
            data = R.get_airlines_by_name(name, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
                
        # Make response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}


    def get_all_countries(self, limit: int = 100, page: int = 0):
        # Retrieve Data and Handle Errors
        pagination = Paginate(per_page=limit, page_number=page)
        try:
            data = R.get_all(DBTables.COUNTRY, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
    
    
    def get_country_by_id(self, id: int):
        # Retrieve Data and Handle Errors
        try:
            data = R.get_by_id(DBTables.COUNTRY, id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ["'id' must be larger than zero."]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            return status.HTTP_404_NOT_FOUND, {'errors': ['The requested resource was not found.']}
        
        # Make response
        return status.HTTP_200_OK, {'data': data}
        

class AnonymousFacade(FacadeBase):
    def __init__(self):
        super().__init__()
        self.__required_group = None
    
    @property 
    def required_group(self):
        return self.__required_group
    
    @staticmethod
    def facade_from_user(user):
        try:
            R.get_or_create_group('admin')
            R.get_or_create_group('airline')
            R.get_or_create_group('customer')
        except Exception as e:
            logger.error("Failed to get/create permission group.")
            raise RepositoryTransactionException("Failed to get/create permission group.")
        
        if is_admin(user):
            return AdministratorFacade(R.serialize_user(user))
        elif is_airline(user):
            return AirlineFacade(R.serialize_user(user))
        elif is_customer(user):
            return CustomerFacade(R.serialize_user(user))
        else:
            return AnonymousFacade()
        
    @staticmethod
    def login(request) -> Union[FacadeBase, str]:
        user = request.user
        if user:
            login(request, user)
            facade = AnonymousFacade.facade_from_user(user)
            if facade:
                return facade, ''
            else:
                return AnonymousFacade(), 'User not assigned to any groups.'
        else:
            return AnonymousFacade(), 'A user with this combination of user/password does not exist.'
    
    def register_customer(self, username, password, email, first_name, last_name, address, phone_number):
        # Create user
        try:
            user, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
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
        
        # Make Response        
        return status.HTTP_200_OK, {'data': {'customer': customer, 'user': user}}

    def get_airlines_by_name(self, name: str = '',  limit: int = 50, page: int = 1):
        """Overrides FacadeBase's function and removes the user information from it.

        Args:
            name (str, optional): Name to filter by. Defaults to empty string ("")
            limit (int, optional): Maximum results per page. Defaults to 50.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            _type_: _description_
        """
        code, data =  super().get_airlines_by_name(name, limit, page)
        if code != 200:
            return code, data
        for airline in data['data']:
            airline.pop('user', None)
        return code, data

class CustomerFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('customer')
        self.__user = user
        
    @property 
    def required_group(self):
        return self.__required_group
        
    def update_customer(self, id, **updated_fields):
        # Retrieve Data and Handle Errors
        try:
            data = R.update(DBTables.CUSTOMER, id, **updated_fields)
        except RepoErrors.FetchError as e:
            res = status.HTTP_404_NOT_FOUND, {'errors': [f"Could not find a customer with the id '{id}'"]}
        except (ValueError, TypeError, ValidationError) as e:
            res = status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            res = handle_unexpected_exception(e)
        else:
            res = status.HTTP_200_OK, {'data':data}
            
        # Return response
        return res


    def add_ticket(self, flight_id: int, seat_count: int):
        # Retrieve Data and Handle Errors
        is_bookable, reason = R.is_flight_bookable(flight_id, seat_count)
        if not is_bookable:
            return status.HTTP_409_CONFLICT, {'errors': [f'Cannot book flight because { reason }.']}
        
        try:
            data, success = R.add(DBTables.TICKET, flight_id=flight_id, customer_id=self.__user['customer'], seat_count=seat_count)
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if success:
            return status.HTTP_200_OK, {'data': data}
        else:
            return status.HTTP_400_BAD_REQUEST, {'errors': data}


    def cancel_ticket(self, ticket_id):
        # Retrieve Data and Handle Errors
        try:
            ticket = R.get_by_id(DBTables, ticket_id)
        except Exception as e:
            return handle_unexpected_exception(e)
            
        # Make and return response
        if not ticket:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Ticket not found.']}
        
        if ticket['customer'] == self.__user['customer']:
            try:
                data = R.update(DBTables.TICKET, id=ticket_id, is_canceled=True)
            except RepoErrors.FetchError:
                return status.HTTP_404_NOT_FOUND, {'errors': ['Ticket not found.']}
            except (ValueError, TypeError, ValidationError) as e:
                return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
            if not data['is_canceled']:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ['Something went wrong when cancelling this ticket.', str(data)]}
            return status.HTTP_200_OK, {'data': data}
        else:
            return status.HTTP_403_FORBIDDEN, {'errors': ['You cannot modify this ticket since it belongs to a different customer.']}

    def get_my_tickets(self, limit: int = 100, page: int = 0):
        # Retrieve Data and Handle Errors
        paginator = Paginate(limit, page)
        # Make Response
        try:
            data = R.get_tickets_by_customer(self.__user['customer'], paginator)
        except Exception as e:
            return handle_unexpected_exception(e)
        return status.HTTP_200_OK, {'data': data, 'pagination': {**paginator}}
    
    def get_airlines_by_name(self, name: str = '',  limit: int = 50, page: int = 1):
        """Overrides FacadeBase's function and removes the user information from it.

        Args:
            name (str, optional): Name to filter by. Defaults to empty string ("")
            limit (int, optional): Maximum results per page. Defaults to 50.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            _type_: _description_
        """
        code, data =  super().get_airlines_by_name(name, limit, page)
        if code != 200:
            return code, data
        for airline in data['data']:
            airline.pop('user', None)
        return code, data
    
    def get_airline_by_id(self, id: int):
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

    def get_my_flights(self, limit: int = 100, page: int = 0):
        # Retrieve Data and Handle Errors
        try:
            data = R.get_flights_by_airline_id(self.__user['airline'])
        except Exception as e:
            return handle_unexpected_exception(e)
        # Make Response
        pagination = Paginate(limit, page)
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}

    def update_airline(self, name: Union[str, None] = None, country_id: Union[int, None] = None):
        # Retrieve Data and Handle Errors
        updated_fields = {}
        if name:
            updated_fields.update(name=name)
        if country_id:
            updated_fields.update(country_id=country_id)
        
        try:
            data = R.update(DBTables.AIRLINECOMPANY, self.__user['airline'], **updated_fields)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Airline not found.']}
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.', str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        return status.HTTP_200_OK, {'data': data}

    def add_flight(self, origin_id: int, destination_id: int, departure_datetime: datetime, arrival_datetime: datetime, total_seats: int):
        # Retrieve Data and Handle Errors
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
        # Make Response
        return status.HTTP_200_OK, {'data': data}

    def update_flight(self, flight_id: int, **updated_fields):
        # Retrieve Data and Handle Errors
        try:
            updated_flight = R.update(DBTables.FLIGHT, id=flight_id, **updated_fields)
        except RepoErrors.FetchError as e:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find flight with ID {flight_id}']}
        except (ValueError, TypeError, ValidationError) as e:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
        except Exception as e:
            return handle_unexpected_exception(e)
        # Make Response
        return status.HTTP_200_OK, {'data': updated_flight}

    def cancel_flight(self, flight_id):
        # Retrieve Data and Handle Errors
        try:
            flight = R.get_by_id(DBTables.FLIGHT, flight_id)
        except Exception as e:
            return handle_unexpected_exception(e)
            
        # Make and return response
        if not flight:
            return status.HTTP_404_NOT_FOUND, {'errors': ['Flight not found.']}
        
        if flight['airline'] == self.__user['airline']:
            try:
                data = R.update(DBTables.FLIGHT, id=flight_id, is_canceled=True)
            except RepoErrors.FetchError:
                return status.HTTP_404_NOT_FOUND, {'errors': ['Flight not found.']}
            except (ValueError, TypeError, ValidationError) as e:
                return status.HTTP_400_BAD_REQUEST, {'errors': ['Error while applying request data.',str(e)]}
            if not data['is_canceled']:
                return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ['Something went wrong when cancelling this flight.', str(data)]}
            return status.HTTP_200_OK, {'data': data}
        else:
            return status.HTTP_403_FORBIDDEN, {'errors': ['You cannot modify this flight since it belongs to a different airline.']}
        
    def get_airlines_by_name(self, name: str = '',  limit: int = 50, page: int = 1):
        """Overrides FacadeBase's function and removes the user information from it.

        Args:
            name (str, optional): Name to filter by. Defaults to empty string ("")
            limit (int, optional): Maximum results per page. Defaults to 50.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            _type_: _description_
        """
        code, data =  super().get_airlines_by_name(name, limit, page)
        if code != 200:
            return code, data
        for airline in data['data']:
            airline.pop('user', None)
        return code, data
    
    def get_airline_by_id(self, id: int):
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
    
    def get_all_customers(self, limit: int = 100, page: int = 1):
        """Returns a JsonResponse object

        Args:
            request (HttpRequest): The request received in the view

        Returns:
            JsonResponse: An object to return from the View
        """
        # Retrieve Data
        pagination = Paginate(per_page=limit, page_number=page)
        try:
            data = R.get_all(DBTables.CUSTOMER, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        return status.HTTP_200_OK, {'data': data, 'pagination': {**pagination}}
        
        
    def add_airline(self, username, password, email, name: str, country_id: int, user_id: int):
        # Create user
        try:
            user, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
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
                
        # Retrieve Data and Handle Errors
        country_exists = R.instance_exists(DBTables.COUNTRY, country_id)
        if not country_exists:
            return status.HTTP_400_BAD_REQUEST, {'errors':[f'Country ID {country_id} not found.']}
        
        user_exists = R.instance_exists(DBTables.USER, user_id)
        if not user_exists:
            return status.HTTP_400_BAD_REQUEST, {'errors':[f'User ID {user_id} not found.']}
        
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
        
        if not success:
            return status.HTTP_400_BAD_REQUEST, {'errors': airline}
        
        # Make Response
        return status.HTTP_200_OK, {'data': {'airline': airline, 'user': user}}
    
    
    def add_customer(self, username: str, password: str, email: str, first_name: str, last_name: str, address: str, phone_number: str):
        # Create user
        try:
            user, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
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
        
        # Make Response
        return status.HTTP_200_OK, {'data': {'customer': customer, 'user': user}}
    
    
    def add_administrator(self, username: str, password: str, email: str, first_name: str, last_name: str):
        # Create user
        try:
            user, user_created = R.add(DBTables.USER, username=username, password=password, email=email)
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
        
        # Make Response
        return status.HTTP_200_OK, {'data': {'admin': admin, 'user': user}}
    
    def deactivate_airline(self, airline_id):
        # Retrieve Data and Handle Errors
        try:
            airline = R.get_by_id(DBTables.AIRLINECOMPANY, airline_id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Airline ID must be greater than 0.']}
        
        if not airline:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find an airline with the ID {airline_id}']}

        try:
            updated = R.update(DBTables.USER, airline['user'], is_active=False)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a user matching an airline with the ID {airline_id}']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if updated['is_active'] == False:
            return status.HTTP_200_OK, {'data': {'success': True}} 
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'data': {'success': False}}
    
    def deactivate_customer(self, customer_id):
        # Retrieve Data and Handle Errors
        try:
            customer = R.get_by_id(DBTables.CUSTOMER, customer_id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Customer ID must be greater than 0.']}
        
        if not customer:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a customer with the ID {customer_id}']}

        try:
            updated = R.update(DBTables.USER, customer['user'], is_active=False)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a user matching a customer with the ID {customer_id}']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if updated['is_active'] == False:
            return status.HTTP_200_OK, {'data': {'success': True}}
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'data': {'success': False}}
        
    
    def deactivate_administrator(self, admin_id):
        # Retrieve Data and Handle Errors
        try:
            admin = R.get_by_id(DBTables.ADMIN, admin_id)
        except RepoErrors.OutOfBoundsException:
            return status.HTTP_400_BAD_REQUEST, {'errors': ['Admin ID must be greater than 0.']}
        
        if not admin:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a admin with the ID {admin_id}']}

        try:
            updated = R.update(DBTables.USER, admin['user'], is_active=False)
        except RepoErrors.FetchError:
            return status.HTTP_404_NOT_FOUND, {'errors': [f'Could not find a user matching a admin with the ID {admin_id}']}
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if updated['is_active'] == False:
            return status.HTTP_200_OK, {'data': {'success': True}}
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {'data': {'success': False}}
    

def handle_unexpected_exception(exception):
    return status.HTTP_500_INTERNAL_SERVER_ERROR, {'errors': ["The server encountered an unexpected error.", str(exception)]}