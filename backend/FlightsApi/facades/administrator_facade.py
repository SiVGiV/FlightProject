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
                            no_content_ok

# Local module imports
from .facade_base import FacadeBase

logger = logging.getLogger('django')

class AdministratorFacade(FacadeBase):
    def __init__(self, user: dict) -> None:
        super().__init__()
        self.__required_group = R.get_or_create_group('admin')
        self.__user = user
        self.__user['admin'] = R.get_by_user_id(DBTables.ADMIN, self.__user['id'])
        
    @property
    def usertype():
        return 'admin'

    @property
    def username(self):
        return self.__user['username']
    
    @property
    def id(self):
        return self.__user['id']

    @property 
    def required_group(self):
        return self.__required_group
    
    def get_customer_by_id(self, id: int):
        """Get a customer's details
        
        Args:
            id (int): Customer's ID

        Returns:
            Tuple[int, dict]: A response tuple containing [status code, response data/errors]
        """
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
            logger.error(e)
            return internal_error_response(errors=e)
        
        # Make response
        return ok_response(data=data, pagination=pagination)
    
    
    def get_airlines_by_name(self, name, limit, page):
        return super().get_airlines_by_name(name, limit, page, allow_deactivated=True)
        
        
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
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not user_created:
            return bad_request_response(errors=user)
        
        user_id = user['id']
        
        # Add user to airline group
        try:
            R.assign_group_to_user(user_id, group_name='airline')
        except RepoErrors.UserAlreadyInGroupException as e:
            logger.error(e)
            return conflict_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
                
        temp_user_data = R.get_by_id(DBTables.USER, user['id'])
        if temp_user_data:
            user = temp_user_data
                
        # Verify country
        country_exists = R.instance_exists(DBTables.COUNTRY, country_id)
        if not country_exists:
            return bad_request_response('Country does not exist')
        
        # Create airline
        try:
            airline, success = R.add(
                DBTables.AIRLINECOMPANY,
                name=name,
                country=country_id,
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
        
        if success:
            data = {'airline': airline, 'user': user}
            return created_response(data)
        else:
            return bad_request_response(errors=airline)
        
    
    
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
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not user_created:
            return bad_request_response(errors=user)
        
        user_id = user['id']
        
        # Add user to customer group
        try:
            R.assign_group_to_user(user_id, group_name='customer')
        except RepoErrors.UserAlreadyInGroupException as e:
            logger.error(e)
            return conflict_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        temp_user_data = R.get_by_id(DBTables.USER, user['id'])
        if temp_user_data:
            user = temp_user_data
        
        # Create customer
        try:
            customer, customer_created = R.add(
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
            return bad_request_response(errors=customer)
        
        data = {'customer': customer, 'user': user}
        
        return created_response(data)
    
    
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
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not user_created:
            return bad_request_response(errors=user)
        
        user_id = user['id']
        
        # Add user to admin group
        try:
            R.assign_group_to_user(user_id, group_name='admin')
        except RepoErrors.UserAlreadyInGroupException as e:
            logger.error(e)
            return conflict_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        temp_user_data = R.get_by_id(DBTables.USER, user['id'])
        if temp_user_data:
            user = temp_user_data
                
        # Create admin
        try:
            admin, success = R.add(
                DBTables.ADMIN,
                first_name=first_name,
                last_name=last_name,
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
        
        if not success:
            return bad_request_response(errors=admin)
        
        data = {'admin': admin, 'user': user}

        return created_response(data)
    
    def deactivate_airline(self, airline_id: int) -> Tuple[int, dict]:
        """Deactivates an airline account

        Args:
            airline_id (int): An airline ID

        Returns:
            Tuple[int, dict]: A status code and data/errors dictionary
        """
        try:
            airline = R.get_by_id(DBTables.AIRLINECOMPANY, airline_id)
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        
        if not airline:
            return not_found_response(errors=RepoErrors.EntityNotFoundException())

        try:
            updated, success = R.update(DBTables.USER, airline['user'], is_active=False)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if updated['is_active'] == False:
            return no_content_ok() 
        else:
            return internal_error_response('Failed to update airline.')
    
    def deactivate_customer(self, customer_id) -> Tuple[int, dict]:
        """Deactivates a customer account

        Args:
            customer_id (int): A customer ID

        Returns:
            Tuple[int, dict]: A status code and data/errors dictionary
        """
        try:
            customer = R.get_by_id(DBTables.CUSTOMER, customer_id)
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not customer:
            return not_found_response(errors=RepoErrors.EntityNotFoundException())

        try:
            updated, success = R.update(DBTables.USER, customer['user'], is_active=False)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)

        if updated['is_active'] == False:
            return no_content_ok()
        else:
            return internal_error_response('Failed to update customer.')


    def deactivate_administrator(self, admin_id) -> Tuple[int, dict]:
        """Deactivates an admin account

        Args:
            admin_id (int): An admin ID

        Returns:
            Tuple[int, dict]: A status code and data/errors dictionary
        """
        try:
            admin = R.get_by_id(DBTables.ADMIN, admin_id)
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not admin:
            return not_found_response(errors=RepoErrors.EntityNotFoundException())

        try:
            updated, success = R.update(DBTables.USER, admin['user'], is_active=False)
        except RepoErrors.FetchError as e:
            logger.error(e)
            return not_found_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        

        if updated['is_active'] == False:
            return no_content_ok()
        else:
            return internal_error_response('Failed to update administrator.')