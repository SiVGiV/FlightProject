# Django imports
from django.db import models
from django.db.models import Model, QuerySet
from django.core.exceptions import ValidationError
from django.utils import timezone
# Local project imports
from ..models import Country, User,\
                   AirlineCompany, Customer, Flight, Ticket
from .errors import *
# Date related imports
from datetime import timedelta
from datetime import date as Date
# Python builtin imports
import logging
from typing import Type, Iterable, Union, List, Dict
from inspect import isclass

logger = logging.getLogger()

def verify_model(func):
    """A decorator to verify that the 1st argument passed to a function is of type Model

    Args:
        func (func): A function to decorate
        
    Raises:
        WrongModelType for types that aren't Model
    """
    def wrapper(*args, **kwargs):
        # Get the model object from the function's arguments
        modelObj = args[0]
        # check if the modelObj is a class: necessary before checking issubclass()
        if not isclass(modelObj): 
            raise WrongModelType("model must be of type Model")
        # Check if the modelObj is a subclass of Model
        if not issubclass(modelObj, Model): 
            raise WrongModelType("model must be of type Model")
        return func(*args, **kwargs)
    return wrapper

def log_action(func):
    """Logs function calls at the debug level

    Args:
        func (function): A function to decorate
    """
    def wrapper(*args, **kwargs):
        logger.debug(f"Called {func.__name__} @ {__name__}")
        func(*args, **kwargs)
    return wrapper
    
class Repository():
    @staticmethod
    @verify_model
    @log_action
    def get_by_id(model: Type[Model], id: int) -> Union[Model, None]:
        """Get item of type model by id

        Args:
            model (type[models.Model]): Model to get row from
            id (int): id of the row to get

        Returns:
            Model object: An item or None if not found
        
        Raises:
            FetchError for bad ID values
        """
        # Validate arguments
        if not isinstance(id, int):
            raise FetchError("id must be an integer")
        if id < 0:
            raise FetchError("id must be larger or equal to 0")
        # Get and return item by id
        return model.objects.filter(pk=id).first()
    
    @staticmethod
    @verify_model
    @log_action
    def get_all(model: Type[Model]) -> QuerySet[Model]:
        """Get all rows from certain model

        Args:
            model (type[Model]): The model to fetch rows from

        Returns:
            list: All rows from model
        """
        return model.objects.all()

    @staticmethod
    @verify_model
    @log_action
    def add(model: Type[Model], **fields) -> Model:
        """Creates and saves an object of the passed model

        Args:
            model (Type[Model]): Model subclass to use for creation

        Raises:
            CreationError: If encounters an error during creation of object

        Returns:
            Model: Created object
        """
        # Try creating the object - expect failure if a field has a mismatching type or value
        try:
            if model == User:
                # Use the .create_user() function for creating users (hashes passwords)
                new_obj = model.objects.create_user(**fields)
            else:
                new_obj = model.objects.create(**fields)
        except (ValueError, TypeError, ValidationError) as e:
            raise CreationError(e)
        else:
            new_obj.save()
        return new_obj
        
    
    @staticmethod
    @verify_model
    @log_action
    def update(model: Type[Model], id: int, **updated_values) -> Model:
        """Update row from model with new data

        Args:
            model (type[Model]): Model to update a row in
            id (int): id of row to update
        KWArgs:
            Any updated values
        Raises:
            UpdateError for non existing attributes, bad attribute types
            FetchError for not found rows
        """
        # Validate argument
        if not isinstance(id, int):
            raise TypeError("id must be of type int.")
        # Check if the item exists before updating it
        item = Repository.get_by_id(model, id)
        if not item:
            raise FetchError("Failed to find an item of model with ID #%i" % id)
        # Update the item's attributes
        for field, value in updated_values.items():
            if hasattr(item, field):
                    setattr(item, field, value)
            else:
                raise UpdateError("Attempted to edit a non existing attribute '%s'." % field)
        # Try to save - this is usually where problems come up (database type validation happens at this stage)
        try:
            item.save()
        except (ValueError, TypeError, ValidationError) as e:
            raise UpdateError("Attempted to set attribute to bad data type/value", e)
        return item
    
    @staticmethod
    @verify_model
    @log_action
    def add_all(model: Type[Model], entry_list: Iterable[Dict]) -> List[Model]:
        """Add all rows to database

        Args:
            model: Table to add the rows to
            new_rows (list): Model objects to add to the database
        
        Returns:
            list of Model objects that were added (Recommended to check if the returned length is the same as the passed length)
        """
        created = []
        for fields in entry_list:
                created.append(Repository.add(model, **fields))
        return created
    
    @staticmethod
    @verify_model
    @log_action
    def remove(model: Type[Model], id: int) -> None:
        """Remove a row from the database

        Args:
            model (Model): the model to remove from
            id (int): The id of the row to remove
        """
        if not isinstance(id, int):
            raise TypeError("id must be of type int.")
        item_to_remove = Repository.get_by_id(model, id)
        if item_to_remove:
            item_to_remove.delete()
    
    @staticmethod
    @log_action
    def get_airline_by_username(username: str) -> Union[AirlineCompany, None]:
        """Get an AirlineCompany from its username

        Args:
            username (str): A username to search for

        Returns:
            AirlineCompany, None: An AirlineCompany object if found, otherwise None
        """
        if not isinstance(username, str):
            raise TypeError("'username' must be of type str.")
        airline = AirlineCompany.objects.filter(user__username=username).first()
        return airline or None
    
    @staticmethod
    @log_action
    def get_customer_by_username(username: str) -> Union[Customer, None]:
        """Get a Customer from its username

        Args:
            username (str): A username to search for

        Returns:
            Customer, None: A Customer object if found, otherwise None
        """
        if not isinstance(username, str):
            raise TypeError("'username' must be of type str.")
        customer = Customer.objects.filter(user__username=username).first()
        return customer or None
    
    @staticmethod
    @log_action
    def get_user_by_username(username: str) -> Union[User, None]:
        """Get a user from its username

        Args:
            username (str): A username to search for

        Raises:
            TypeError: If passed anything other than a str

        Returns:
            : _description_
        """
        if not isinstance(username, str):
            raise TypeError("'username' must be of type str.")
        user = User.objects.filter(username=username).first()
        return user or None
    
    @staticmethod
    @log_action
    def get_flights_by_parameters(origin_country_id: int, destination_country_id: int, date: Date) -> Union[QuerySet[Flight], None]:
        """Returns a QuerySet for flights that fit the parameters

        Args:
            origin_country_id (int): id field of the origin country
            destination_country_id (int): id field of the destination country
            date (date): date of departure

        Raises:
            TypeError: for 'origin_country_id' that isn't an int
            TypeError: for 'destination_country_id' that isn't an int
            TypeError: for 'date' that isn't a date object

        Returns:
            QuerySet[Flight]: A QuerySet object containing all query results
        """
        if not isinstance(origin_country_id, int):
            raise TypeError("'origin_country_id' must be of type int")
        if not isinstance(destination_country_id, int):
            raise TypeError("'destination_country_id' must be of type int")
        if not isinstance(date, Date):
            raise TypeError("'date' must be of type Date")
        query = Flight.objects.filter(origin_country__id=origin_country_id)
        query = query.filter(destination_country__id = destination_country_id)
        query = query.filter(departure_datetime__date = date)
        return query.all()
    
    @staticmethod
    @log_action
    def get_flights_by_airline_id(airline_id: int) -> QuerySet[Flight]:
        """Fetch 

        Args:
            airline_id (int): An airline ID

        Raises:
            TypeError: In case of a non-integer airline_id

        Returns:
            QuerySet[Flight]: A QuerySet manager containing flights owned by the airline
        """
        if not isinstance(airline_id, int):
            raise TypeError("'airline_id' must be of type 'int'.")
        flights = Flight.objects.filter(airline__pk=airline_id).all()
        return flights
    
    @staticmethod
    @log_action
    def get_arrival_flights(country_id: int) -> QuerySet[Flight]:
        """Get all flights arriving to a country in the next 12 hours

        Args:
            country_id (int): ID of the country

        Raises:
            TypeError: if country_id is not int

        Returns:
            QuerySet[Flight]: Collection of flights
        """
        if not isinstance(country_id, int):
            raise TypeError("'country_id' must be of type 'int'.")
        country = Country.objects.filter(pk=country_id).first()
        if not country:
            return [] # Return empty iterable as to not crash iterators
        query = Flight.objects.filter(destination_country__id=country_id)
        query = query.filter(arrival_datetime__gte=timezone.now())
        query = query.filter(arrival_datetime__lte=timezone.now() + timedelta(hours=12))
        return query.all()
    
    @staticmethod
    @log_action
    def get_departure_flights(country_id: int) -> QuerySet[Flight]:
        """Get all flights leaving a country in the next 12 hours

        Args:
            country_id (int): ID of the country

        Raises:
            TypeError: if country_id is not int

        Returns:
            QuerySet[Flight]: Collection of flights
        """
        if not isinstance(country_id, int):
            raise TypeError("'country_id' must be of type 'int'.")
        country = Country.objects.filter(pk=country_id).first()
        if not country:
            return None
        query = Flight.objects.filter(origin_country__id=country_id)
        query = query.filter(departure_datetime__gte=timezone.now())
        query = query.filter(departure_datetime__lte=timezone.now() + timedelta(hours=12))
        return query.all()
    
    @staticmethod
    @log_action
    def get_tickets_by_customer(customer_id: int) -> QuerySet[Ticket]:
        """Fetches all tickets belonging to a customer

        Args:
            customer_id (int): Id of the customer

        Raises:
            TypeError: If customer_id is not 'int'

        Returns:
            QuerySet[Ticket]: Collection of tickets
        """
        if not isinstance(customer_id, int):
            raise TypeError("'customer_id' must be of type 'int'.")
        tickets = Ticket.objects.filter(customer__id=customer_id)
        return tickets.all()
    
    @staticmethod
    @log_action
    def get_airlines_by_country(country_id: int) -> QuerySet[AirlineCompany]:
        """Get all airlines in a certain country

        Args:
            country_id (int): The country's ID

        Raises:
            TypeError: If 'country_id' is not of type 'int'

        Returns:
            QuerySet[AirlineCompany]: A QuerySet of AirlineCompany objects
        """
        if not isinstance(country_id, int):
            raise TypeError("'country_id' must be of type 'int'.")
        airlines = AirlineCompany.objects.filter(country__id=country_id)
        return airlines.all()
    
    @staticmethod
    @log_action
    def get_flights_by_origin(country_id: int) -> QuerySet[Flight]:
        """Get flights that take off from a certain country

        Args:
            country_id (int): ID of the country

        Raises:
            TypeError: if 'country_id' is not an 'int'

        Returns:
            QuerySet[Flight]: A QuerySet of Flight objects
        """
        if not isinstance(country_id, int):
            raise TypeError("'country_id' must be of type 'int'.")
        results = Flight.objects.filter(origin_country__id=country_id)
        return results.all()
    
    @staticmethod
    @log_action
    def get_flights_by_destination(country_id: int) -> QuerySet[Flight]:
        """Get flights that land in a certain country

        Args:
            country_id (int): ID of the country

        Raises:
            TypeError: if 'country_id' is not an 'int'

        Returns:
            QuerySet[Flight]: A QuerySet of Flight objects
        """
        if not isinstance(country_id, int):
            raise TypeError("'country_id' must be of type 'int'.")
        results = Flight.objects.filter(destination_country__id=country_id)
        return results.all()
    
    @staticmethod
    @log_action
    def get_flights_by_departure_date(date: Date) -> QuerySet[Flight]:
        """Get flights that depart on a certain date

        Args:
            date (Date): a date object to check on 

        Raises:
            TypeError: If 'date' is not of type 'datetime.date'

        Returns:
            QuerySet[Flight]: QuerySet of Flight objects
        """
        if not isinstance(date, Date):
            raise TypeError("'date' must be of type 'datetime.date'.")
        flights = Flight.objects.filter(departure_datetime__date=date)
        return flights.all()
    
    @staticmethod
    @log_action
    def get_flights_by_arrival_date(date: Date) -> QuerySet[Flight]:
        """Get flights that arrive on a certain date

        Args:
            date (Date): a date object to check on 

        Raises:
            TypeError: If 'date' is not of type 'datetime.date' 

        Returns:
            QuerySet[Flight]: QuerySet of Flight objects
        """
        if not isinstance(date, Date):
            raise TypeError("'date' must be of type 'datetime.date'.")
        flights = Flight.objects.filter(arrival_datetime__date=date)
        return flights.all()
    
    @staticmethod
    @log_action
    def get_flights_by_customer(customer_id: int) -> QuerySet[Flight]:
        """Fetch all flights for a customer

        Args:
            customer_id (int): ID of the customer

        Raises:
            TypeError: If 'customer_id' is not of type 'int'

        Returns:
            QuerySet[Flight]: A QuerySet of Flight objects
        """
        if not isinstance(customer_id, int):
            raise TypeError()
        flights = Flight.objects.filter(tickets__customer__id=customer_id)
        return flights.all()
