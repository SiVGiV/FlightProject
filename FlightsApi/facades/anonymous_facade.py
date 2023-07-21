# Python builtin imports
from typing import Tuple
import logging

# Django imports
from django.contrib.auth import login
from django.http import HttpRequest
from django.core.exceptions import ValidationError

# App imports
from FlightsApi.repository import Repository as R, DBTables
from FlightsApi.repository import errors as RepoErrors
from FlightsApi.utils import is_customer, is_airline, is_admin
from FlightsApi.utils.response_utils import conflict_response, bad_request_response, \
                            created_response, internal_error_response

# Local module imports
from .errors import *
from .facade_base import FacadeBase
from .administrator_facade import AdministratorFacade
from .airline_facade import AirlineFacade
from .customer_facade import CustomerFacade

logger = logging.getLogger('django')

class AnonymousFacade(FacadeBase):
    """
    An anonymous user serving class.
    """
    __groups_created = False
    def __init__(self):
        super().__init__()
        self.__required_group = None # Anonymous users do not need to be a part of a group
    
    @staticmethod
    def usertype():
        return 'anon'
    
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
        if not AnonymousFacade.__groups_created:
            try:
                R.get_or_create_group('admin')
                R.get_or_create_group('airline')
                R.get_or_create_group('customer')
            except Exception as e:
                logger.error(e)
                raise RepositoryTransactionException("Failed to get/create permission group.\n" + str(e))
            else:
                AnonymousFacade.__groups_created = True
        
        # Return the right facade
        if is_admin(user):
            return AdministratorFacade(R.serialize_user(user))
        elif is_airline(user):
            return AirlineFacade(R.serialize_user(user))
        elif is_customer(user):
            return CustomerFacade(R.serialize_user(user))
        else:
            if user.is_superuser:
                R.assign_group_to_user(user.id, 'admin')
                return AdministratorFacade(R.serialize_user(user))
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
                request.COOKIES['usertype'] = 'anon'
                return AnonymousFacade(), ''
            login(request, user) # Django login function
            facade = AnonymousFacade.facade_from_user(user)
            if facade:
                request.COOKIES['usertype'] = facade.usertype()
                return facade, '' # Return the right facade and an empty reason.
            else:
                request.COOKIES['usertype'] = 'anon'
                return AnonymousFacade(), 'User not assigned to any groups.'
        else:
            request.COOKIES['usertype'] = 'anon'
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
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not user_created:
            return bad_request_response(errors=user_data)
        
        user_id = user_data['id']
        
        # Add user to customer group
        try:
            R.assign_group_to_user(user_id, group_name='customer')
        except RepoErrors.UserAlreadyInGroupException as e:
            logger.error(e)
            return conflict_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        temp_user_data = R.get_by_id(DBTables.USER, user_data['id'])
        if temp_user_data:
            user_data = temp_user_data
        
        # Create customer
        try:
            customer_data, customer_created = R.add(
                DBTables.CUSTOMER,
                first_name=first_name,
                last_name=last_name,
                address=address,
                phone_number=phone_number,
                user=user_id
            )
        except (ValueError, TypeError, ValidationError) as e:
            logger.error(e)
            R.remove(DBTables.USER, user_id)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            R.remove(DBTables.USER, user_id)
            return internal_error_response(errors=e)
        
        if not customer_created:
            return bad_request_response(errors=customer_data)

        data = {'customer': customer_data, 'user': user_data}
        # Return response
        return created_response(data)

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
