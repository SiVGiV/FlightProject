from abc import abstractmethod, abstractproperty
from datetime import date as Date
from typing import Tuple
import logging

from ..repository import Repository as R, DBTables, Paginate
from ..repository import errors as RepoErrors
from ..utils.response_utils import not_found_response, bad_request_response, \
                            ok_response, internal_error_response

logger = logging.getLogger('django')

class FacadeBase():
    @abstractproperty
    def usertype(self):
        pass
        
    @abstractproperty
    def required_group(self):
        """
        A required property getter to be overridden by inheriting classes.
        """
        pass
    
    @abstractproperty
    def username(self):
        pass
    
    @abstractproperty
    def id(self):
        pass
    
    @abstractproperty
    def entity_id(self):
        pass
    
    @abstractproperty
    def entity_name(self):
        pass
    
    def whoami(self):
        """
        Returns the type, username and ID of the user.
        
        
        """
        data = {
            'logged_in': self.usertype != 'anon',
            'id': self.id,
            'type': self.usertype,
            'username': self.username,
            'entity_id': self.entity_id,
            'entity_name': self.entity_name
        }
        return ok_response(data=data)
        
    
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
            logger.error(e)
            return internal_error_response(errors=e)
        
        # Return response
        return ok_response(data=data, pagination=pagination)
    
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
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not data: # Check if the result came up empty
            return not_found_response(errors=RepoErrors.EntityNotFoundException())
        
        # Return response
        return ok_response(data=data)
    
    @staticmethod
    def get_flights_by_parameters(origin_country_id: int = None, destination_country_id: int = None, date: Date = None, airline_id: int = None, limit: int = 50, page: int = 1, allow_cancelled: bool = True) -> Tuple[int, dict]:
        """Get all flights and filter by given parameters.

        Args:
            origin_country_id (int, optional): Id of the flight's origin country. Defaults to None.
            destination_country_id (int, optional): Id of the flight's destination country. Defaults to None.
            date (Date, optional): Date of departure. Defaults to None.
            airline_id (int, optional): Id of the flight's operating airline. Defaults to None.
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 1.

        Returns:
            Tuple[int, dict]: Status code, data
        """
        # Initialize pagination
        pagination = Paginate(limit, page)
        
        # Fetch data and handle exceptions
        try:
            data = R.get_flights_by_parameters(origin_country_id, destination_country_id, date, airline_id, allow_cancelled, pagination)
        except ValueError as e:
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        # Return response
        return ok_response(data=data, pagination=pagination)
        
    @classmethod
    def get_all_airlines(cls, limit: int = 50, page: int = 1) -> Tuple[int, dict]:
        """Get all airlines

        Args:
            limit (int, optional): Pagination limit. Defaults to 50.
            page (int, optional): Pagination page. Defaults to 1.

        Returns:
            Tuple[int, dict]: Status code, data
        """
        cls.get_airlines_by_name('', limit=limit, page=page)
    
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
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not data: # Check if the result came up empty
            return not_found_response(errors=RepoErrors.EntityNotFoundException())
        
        # Return response
        return ok_response(data=data)
    
    @staticmethod
    def get_airlines_by_name(name: str, limit: int = 50, page: int = 1, allow_deactivated = False) -> Tuple[int, dict]:
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
            data = R.get_airlines_by_name(name, pagination, allow_deactivated)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
                
        # Return response
        return ok_response(data=data, pagination=pagination)

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
            logger.error(e)
            return internal_error_response(errors=e)
        
        # Return response
        return ok_response(data=data, pagination=pagination)
    
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
        except RepoErrors.OutOfBoundsException as e:
            logger.error(e)
            return bad_request_response(errors=e)
        except Exception as e:
            logger.error(e)
            return internal_error_response(errors=e)
        
        if not data: # Check if the result came up empty
            return not_found_response(errors=RepoErrors.EntityNotFoundException())
        
        # Return response
        return ok_response(data=data)
        
