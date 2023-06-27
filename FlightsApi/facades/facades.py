from ..repository import Repository as R, DBTables, Paginate
from ..repository import errors as RepoErrors
from ..utils import log_action
from datetime import datetime, date as Date
from typing import Union
from abc import abstractmethod
from django.contrib.auth import authenticate
from .errors import *
from .response_utils import FacadeResponse
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
        res = FacadeResponse(200, data=data, pagination={**pagination})
        
        # Return response
        return res.renderJSON()
    
    
    def get_flight_by_id(self, id: int):
        # Retrieve Data and Handle Errors
        try:
            data = R.get_by_id(DBTables.FLIGHT, id)
        except RepoErrors.OutOfBoundsException:
            res = FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=["'id' must be larger than zero."])
            return res.renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            res = FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['The requested resource was not found.'])
            return res.renderJSON()
        
        # Make response
        res = FacadeResponse(200, data=data)
        
        # Return response
        return res.renderJSON()
    
    
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
        res = FacadeResponse(200, data=data, pagination={**pagination})
        # Return Response
        return res.renderJSON()
        
        
    def get_all_airlines(self,  limit: int = 100, page: int = 1):
        # Retrieve Data and Handle Errors
        pagination = Paginate(per_page=limit, page_number=page)
        try:
            data = R.get_all(DBTables.AIRLINECOMPANY, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        res = FacadeResponse(200, data=data, pagination={**pagination})
        
        # Return response
        return res.renderJSON()
    
    
    def get_airline_by_id(self, id: int):
        # Retrieve Data and Handle Errors
        try:
            data = R.get_by_id(DBTables.AIRLINECOMPANY, id)
        except RepoErrors.OutOfBoundsException:
            res = FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=["'id' must be larger than zero."])
            return res.renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            res = FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['The requested resource was not found.'])
            return res.renderJSON()
        
        # Make response
        res = FacadeResponse(200, data=data)
        
        # Return response
        return res.renderJSON()
    
    
    def get_airlines_by_name(self, name: str, limit: int = 100, page: int = 1):
        # Retrieve Data and Handle Errors
        pagination = Paginate(limit, page)
        try:
            data = R.get_airlines_by_name(name, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
                
        # Make response
        res = FacadeResponse(200, data=data, pagination={**pagination})
        
        # Return response
        return res.renderJSON()


    def get_all_countries(self, limit: int = 100, page: int = 0):
        # Retrieve Data and Handle Errors
        pagination = Paginate(per_page=limit, page_number=page)
        try:
            data = R.get_all(DBTables.COUNTRY, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        res = FacadeResponse(200, data=data, pagination={**pagination})
        
        # Return response
        return res.renderJSON()
    
    
    def get_country_by_id(self, id: int):
        # Retrieve Data and Handle Errors
        try:
            data = R.get_by_id(DBTables.COUNTRY, id)
        except RepoErrors.OutOfBoundsException:
            res = FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=["'id' must be larger than zero."])
            return res.renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        if not data: # Check if the result came up empty
            res = FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['The requested resource was not found.'])
            return res.renderJSON()
        
        # Make response
        res = FacadeResponse(200, data=data)
        
        # Return response
        return res.renderJSON()
    
    @staticmethod
    def create_new_user(username: str, password: str, email: str):
        try:
            data, success = R.add(DBTables.USER, username=username, password=password, email=email)
        except (ValueError, TypeError, ValidationError) as e:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        return data, success
        

class AnonymousFacade(FacadeBase):
    def __init__(self, user):
        super().__init__()
        self.__required_group = None
    
    @property 
    def required_group(self):
        return self.__required_group
    
    def facade_from_user(self, user: dict):
        try:
            admin_id = R.get_or_create_group('admin')['id']
            airline_id = R.get_or_create_group('airline')['id']
            customer_id = R.get_or_create_group('customer')['id']
        except Exception as e:
            logger.error("Failed to get/create permission group.")
            raise RepositoryTransactionException("Failed to get/create permission group.")
        
        if admin_id in user['groups']:
            return AdministratorFacade(user)
        elif airline_id in user['groups']:
            return AirlineFacade(user)
        elif customer_id in user['groups']:
            return CustomerFacade(user)
        else:
            return None
        
    def login(self, request, username, password):
        user = R.authenticate(request=request, username=username, password=password)
        if user:
            facade = self.facade_from_user(user)
            return facade or None
        return None


class CustomerFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('customer')
        self.__user = user
        
    @property 
    def required_group(self):
        return self.__required_group
        
    def update_customer(self, request, id, **updated_fields):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        if not self.__user['customer']['id'] == id:
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=["You cannot edit another user's details."])
            return res.renderJSON()
        
        # Retrieve Data and Handle Errors
        try:
            data = R.update(DBTables.CUSTOMER, id, **updated_fields)
        except RepoErrors.FetchError as e:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f"Could not find a customer with the id '{id}'"]).renderJSON()
        except (ValueError, TypeError, ValidationError) as e:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        res = FacadeResponse(200, data=data)
        
        # Return response
        return res.renderJSON()


    def add_ticket(self, request, flight_id: int, seat_count: int):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        
        # Retrieve Data and Handle Errors
        is_bookable, reason = R.is_flight_bookable(flight_id, seat_count)
        if not is_bookable:
            res = FacadeResponse(status.HTTP_409_CONFLICT, errors=[f'Cannot book flight because { reason }.'])
        
        try:
            data, success = R.add(DBTables.TICKET, flight_id=flight_id, customer_id=self.__user['customer'], seat_count=seat_count)
        except (ValueError, TypeError, ValidationError) as e:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if success:
            res = FacadeResponse(status.HTTP_200_OK, data=data)
        else:
            res = FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=data)
            
        # Return Response
        return res.renderJSON()

    def cancel_ticket(self, request, ticket_id):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        try:
            ticket = R.get_by_id(DBTables, ticket_id)
        except Exception as e:
            return handle_unexpected_exception(e)
            
        # Make and return response
        if not ticket:
            res = FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['Ticket not found.']).renderJSON()
            return res
        
        if ticket['customer'] == self.__user['customer']:
            try:
                data = R.update(DBTables.TICKET, id=ticket_id, is_canceled=True)
            except RepoErrors.FetchError:
                return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['Ticket not found.']).renderJSON()
            except (ValueError, TypeError, ValidationError) as e:
                return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
            if not data['is_canceled']:
                return FacadeResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, errors=['Something went wrong when cancelling this ticket.', str(data)]).renderJSON()
            return FacadeResponse(status.HTTP_200_OK, data=data).renderJSON()
        else:
            return FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['You cannot modify this ticket since it belongs to a different customer.']).renderJSON()

    def get_my_tickets(self, request, limit: int = 100, page: int = 0):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        paginator = Paginate(limit, page)
        # Make Response
        try:
            data = R.get_tickets_by_customer(self.__user['customer'], paginator)
        except Exception as e:
            return handle_unexpected_exception(e)
        res = FacadeResponse(status.HTTP_200_OK, data=data, pagination={**paginator})
        # Return Response
        return res.renderJSON()


class AirlineFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('airlinecompany')
        self.__user = user
    
    @property 
    def required_group(self):
        return self.__required_group

    def get_my_flights(self, request, limit: int = 100, page: int = 0):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        if not request.user.is_authenticated() or not self.__user['id'] == request.user.id:
            res = FacadeResponse(status.HTTP_401_UNAUTHORIZED, errors=['Not authorized.'])
        
        # Retrieve Data and Handle Errors
        try:
            data = R.get_flights_by_airline_id(self.__user['airline'])
        except Exception as e:
            return handle_unexpected_exception(e)
        # Make Response
        pagination = Paginate(limit, page)
        res = FacadeResponse(status.HTTP_200_OK, data=data, pagination={**pagination})    
        # Return Response
        return res.renderJSON()

    def update_airline(self, request, name: Union[str, None] = None, country_id: Union[int, None] = None):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        updated_fields = {}
        if name:
            updated_fields.update(name=name)
        if country_id:
            updated_fields.update(country_id=country_id)
        
        try:
            data = R.update(DBTables.AIRLINECOMPANY, self.__user['airline'], **updated_fields)
        except RepoErrors.FetchError:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['Airline not found.']).renderJSON()
        except (ValueError, TypeError, ValidationError) as e:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        res = FacadeResponse(status.HTTP_200_OK, data=data)
        # Return Response
        return res.renderJSON()

    def add_flight(self, request, origin_id: int, destination_id: int, departure_datetime: datetime, arrival_datetime: datetime, total_seats: int):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()

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
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        if not success:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=data).renderJSON()
        # Make Response
        res = FacadeResponse(status.HTTP_200_OK, data=data)
        # Return Response
        return res.renderJSON()

    def update_flight(self, request, flight_id: int, **updated_fields):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        try:
            updated_flight = R.update(DBTables.FLIGHT, id=flight_id, **updated_fields)
        except RepoErrors.FetchError as e:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f'Could not find flight with ID {flight_id}']).renderJSON()
        except (ValueError, TypeError, ValidationError) as e:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        # Make Response
        res = FacadeResponse(status.HTTP_200_OK, data=updated_flight)
        # Return Response
        return res.renderJSON()

    def cancel_flight(self, request, flight_id):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        try:
            flight = R.get_by_id(DBTables.FLIGHT, flight_id)
        except Exception as e:
            return handle_unexpected_exception(e)
            
        # Make and return response
        if not flight:
            res = FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['Flight not found.']).renderJSON()
            return res
        
        if flight['airline'] == self.__user['airline']:
            try:
                data = R.update(DBTables.FLIGHT, id=flight_id, is_canceled=True)
            except RepoErrors.FetchError:
                return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=['Flight not found.']).renderJSON()
            except (ValueError, TypeError, ValidationError) as e:
                return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
            if not data['is_canceled']:
                return FacadeResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, errors=['Something went wrong when cancelling this flight.', str(data)]).renderJSON()
            return FacadeResponse(status.HTTP_200_OK, data=data).renderJSON()
        else:
            return FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['You cannot modify this flight since it belongs to a different airline.']).renderJSON()


class AdministratorFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('admin')
        self.__user = user

    @property 
    def required_group(self):
        return self.__required_group
    
    def get_all_customers(self, request, limit: int = 100, page: int = 1):
        """Returns a JsonResponse object

        Args:
            request (HttpRequest): The request received in the view

        Returns:
            JsonResponse: An object to return from the View
        """
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        
        # Retrieve Data
        pagination = Paginate(per_page=limit, page_number=page)
        try:
            data = R.get_all(DBTables.CUSTOMER, pagination)
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make response
        res = FacadeResponse(200, data=data, pagination={**pagination})
        
        # Return response
        return res.renderJSON()
        
        
    def add_airline(self, request, name: str, country_id: int, user_id: int):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        
        # Retrieve Data and Handle Errors
        country_exists = R.instance_exists(DBTables.COUNTRY, country_id)
        if not country_exists:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=[f'Country ID {country_id} not found.']).renderJSON()
        
        user_exists = R.instance_exists(DBTables.USER, user_id)
        if not user_exists:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=[f'User ID {user_id} not found.']).renderJSON()
        
        # Add user to airline group
        try:
            R.assign_group_to_user(user_id, group_name='airline')
        except RepoErrors.EntityNotFoundException:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=[f'User ID {user_id} not found.']).renderJSON()
        except RepoErrors.UserAlreadyInGroupException:
            return FacadeResponse(status.HTTP_409_CONFLICT, errors=[f'User ID {user_id} is already assigned to a role.']).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        
        try:
            data, success = R.add(
                DBTables.AIRLINECOMPANY,
                name=name,
                country_id=country_id,
                user_id=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return handle_unexpected_exception(e)
        
        if not success:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=data).renderJSON()
        
        # Make Response
        res = FacadeResponse(status.HTTP_200_OK, data=data)
        
        # Return Response
        return res.renderJSON()
    
    def add_customer(self, request, user_id: int, first_name: str, last_name: str, address: str, phone_number: str):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        
        user_exists = R.instance_exists(DBTables.USER, user_id)
        if not user_exists:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=[f'User ID {user_id} not found.']).renderJSON()
        
        # Add user to customer group
        try:
            R.assign_group_to_user(user_id, group_name='customer')
        except RepoErrors.EntityNotFoundException:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=[f'User ID {user_id} not found.']).renderJSON()
        except RepoErrors.UserAlreadyInGroupException:
            return FacadeResponse(status.HTTP_409_CONFLICT, errors=[f'User ID {user_id} is already assigned to a role.']).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        try:
            data, success = R.add(
                DBTables.CUSTOMER,
                first_name=first_name,
                last_name=last_name,
                address=address,
                phone_number=phone_number,
                user_id=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.',str(e)]).renderJSON()
        except Exception as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return handle_unexpected_exception(e)
        
        if not success:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=data).renderJSON()
        
        # Make Response
        res = FacadeResponse(status.HTTP_200_OK, data=data)
        
        # Return Response
        return res.renderJSON()
    
    
    def add_administrator(self, request, user_id: int, first_name: str, last_name: str):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        
        user_exists = R.instance_exists(DBTables.USER, user_id)
        if not user_exists:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=[f'User ID {user_id} not found.']).renderJSON()
        
        # Add user to admin group
        try:
            R.assign_group_to_user(user_id, group_name='admin')
        except RepoErrors.EntityNotFoundException:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=[f'User ID {user_id} not found.']).renderJSON()
        except RepoErrors.UserAlreadyInGroupException:
            return FacadeResponse(status.HTTP_409_CONFLICT, errors=[f'User ID {user_id} is already assigned to a role.']).renderJSON()
        except Exception as e:
            return handle_unexpected_exception(e)
        
        try:
            data, success = R.add(
                DBTables.ADMIN,
                first_name=first_name,
                last_name=last_name,
                user_id=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Error while applying request data.', str(e)]).renderJSON()
        except Exception as e:
            R.assign_group_to_user(user_id, '') # undo the addition of a group
            return handle_unexpected_exception(e)
        
        if not success:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=data).renderJSON()
        
        # Make Response
        res = FacadeResponse(status.HTTP_200_OK, data=data)
        
        # Return Response
        return res.renderJSON()
    
    def deactivate_airline(self, request, airline_id):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        try:
            airline = R.get_by_id(DBTables.AIRLINECOMPANY, airline_id)
        except RepoErrors.OutOfBoundsException:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Airline ID must be greater than 0.'])
        
        if not airline:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f'Could not find an airline with the ID {airline_id}'])

        try:
            updated = R.update(DBTables.USER, airline['user'], is_active=False)
        except RepoErrors.FetchError:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f'Could not find a user matching an airline with the ID {airline_id}'])
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if updated['is_active'] == False:
            res = FacadeResponse(status.HTTP_200_OK, data={'success': True})    
        else:
            res = FacadeResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, data={'success': False})    
        # Return Response
        return res
    
    def deactivate_customer(self, request, customer_id):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        try:
            customer = R.get_by_id(DBTables.CUSTOMER, customer_id)
        except RepoErrors.OutOfBoundsException:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Customer ID must be greater than 0.'])
        
        if not customer:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f'Could not find a customer with the ID {customer_id}'])

        try:
            updated = R.update(DBTables.USER, customer['user'], is_active=False)
        except RepoErrors.FetchError:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f'Could not find a user matching a customer with the ID {customer_id}'])
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if updated['is_active'] == False:
            res = FacadeResponse(status.HTTP_200_OK, data={'success': True})    
        else:
            res = FacadeResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, data={'success': False})    
        # Return Response
        return res
        
    
    def deactivate_administrator(self, request, admin_id):
        # Verify Permissions
        if not has_permission(self, request):
            res = FacadeResponse(status.HTTP_403_FORBIDDEN, errors=['Missing permissions.'])
            return res.renderJSON()
        # Retrieve Data and Handle Errors
        try:
            admin = R.get_by_id(DBTables.ADMIN, admin_id)
        except RepoErrors.OutOfBoundsException:
            return FacadeResponse(status.HTTP_400_BAD_REQUEST, errors=['Admin ID must be greater than 0.'])
        
        if not admin:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f'Could not find a admin with the ID {admin_id}'])

        try:
            updated = R.update(DBTables.USER, admin['user'], is_active=False)
        except RepoErrors.FetchError:
            return FacadeResponse(status.HTTP_404_NOT_FOUND, errors=[f'Could not find a user matching a admin with the ID {admin_id}'])
        except Exception as e:
            return handle_unexpected_exception(e)
        
        # Make Response
        if updated['is_active'] == False:
            res = FacadeResponse(status.HTTP_200_OK, data={'success': True})    
        else:
            res = FacadeResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, data={'success': False})    
        # Return Response
        return res
    

def has_permission(facade, request):
    if request.user.has_perm('is_' + facade.required_group['name']):
        return True
    else:
        return False


def handle_unexpected_exception(exception):
    res = FacadeResponse(status.HTTP_500_INTERNAL_SERVER_ERROR, errors=["The server encountered an unexpected error.", str(exception)])
    return res.renderJSON()