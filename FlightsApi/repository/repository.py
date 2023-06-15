# Django imports
from django.db.models import Model, QuerySet
from django.core.exceptions import ValidationError
from django.utils import timezone
# Local project imports
from ..models import Country, User,\
                   AirlineCompany, Customer, Flight, Ticket
from .errors import *
from ..utils import accepts, log_action
# Date related imports
from datetime import timedelta
from datetime import date as Date
# Python builtin imports
import logging
from typing import Type, Iterable, Union, List, Dict

logger = logging.getLogger()

class Repository():
    @staticmethod
    @log_action
    @accepts(int, model=True, throw=FetchError)
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
        if id < 0:
            raise FetchError("id must be larger or equal to 0")
        
        # Get and return item by id
        return model.objects.filter(pk=id).first()
    
    @staticmethod
    @log_action
    @accepts(model=True, throw=FetchError)
    def get_all(model: Type[Model]) -> QuerySet[Model]:
        """Get all rows from certain model

        Args:
            model (type[Model]): The model to fetch rows from

        Returns:
            list: All rows from model
        """
        return model.objects.all()

    @staticmethod
    @log_action
    @accepts(model=True, throw=CreationError)
    def add(model: Type[Model], **fields) -> Model:
        """Creates and saves an object of the passed model

        Args:
            model (Type[Model]): Model subclass to use for creation

        Raises:
            CreationError: If encounters an error during creation of object

        Returns:
            Model: Created object
        """
        # Try creating the object - expects failure if a field has a mismatching type or value
        new_obj = None
        try:
            if model == User:
                # Use the .create_user() function for creating users (hashes passwords)
                new_obj = model.objects.create_user(**fields)
            else:
                new_obj = model.objects.create(**fields)
        except (ValueError, TypeError, ValidationError) as e:
            raise CreationError(e)
        return new_obj
    
    @staticmethod
    @log_action
    @accepts(int, model=True, throw=UpdateError)
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
        # Get the item
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
    @log_action
    @accepts(model=True)
    def add_all(model: Type[Model], entry_list: Iterable[Dict]) -> List[Model]:
        """Add all rows to database

        Args:
            model: Table to add the rows to
            new_rows (list): Model objects to add to the database
        
        Returns:
            list of Model objects that were added 
            It is recommended to check if the returned length is the same as the passed length
        """
        created = []
        for fields in entry_list:
            try:
                # Only appends the successful additions
                created.append(Repository.add(model, **fields))
            except CreationError as e:
                logger.warning("Failed object creation.\n", exc_info=e)
        # Return all created objects
        return created
    
    @staticmethod
    @log_action
    @accepts(int, model=True)
    def remove(model: Type[Model], id: int) -> None:
        """Remove a row from the database

        Args:
            model (Model): the model to remove from
            id (int): The id of the row to remove
        """
        # Get the item
        try:
            item_to_remove = Repository.get_by_id(model, id)
        except FetchError as e:
            logger.warning("Couldn't fetch item to delete.", exc_info=e)
            item_to_remove = None
            
        # If an item was found, delete it
        if item_to_remove:
            item_to_remove.delete()
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_airline_by_username(username: str) -> Union[AirlineCompany, None]:
        """Get an AirlineCompany from its username

        Args:
            username (str): A username to search for

        Returns:
            AirlineCompany, None: An AirlineCompany object if found, otherwise None
        """
        airline = AirlineCompany.objects.filter(user__username=username).first()
        return airline or None
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_customer_by_username(username: str) -> Union[Customer, None]:
        """Get a Customer from its username

        Args:
            username (str): A username to search for

        Returns:
            Customer, None: A Customer object if found, otherwise None
        """
        customer = Customer.objects.filter(user__username=username).first()
        return customer or None
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_user_by_username(username: str) -> Union[User, None]:
        """Get a user from its username

        Args:
            username (str): A username to search for

        Returns:
            User: A User model object (or None)
        """
        user = User.objects.filter(username=username).first()
        return user or None
    
    @staticmethod
    @log_action
    @accepts(int, int, Date)
    def get_flights_by_parameters(origin_country_id: int, destination_country_id: int, date: Date) -> Union[QuerySet[Flight], None]:
        """Returns a QuerySet for flights that fit the parameters

        Args:
            origin_country_id (int): id field of the origin country
            destination_country_id (int): id field of the destination country
            date (date): date of departure

        Returns:
            QuerySet[Flight]: A QuerySet object containing all query results
        """
        # Get all flights that take off from origin_country
        query = Flight.objects.filter(origin_country__id=origin_country_id)
        # Of those flights, get the ones that go to destination_country
        query = query.filter(destination_country__id = destination_country_id)
        # Finally, of those fflights get any that depart on the specified date
        query = query.filter(departure_datetime__date = date)
        
        return query.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_airline_id(airline_id: int) -> QuerySet[Flight]:
        """Fetch 

        Args:
            airline_id (int): An airline ID

        Returns:
            QuerySet[Flight]: A QuerySet manager containing flights owned by the airline
        """
        flights = Flight.objects.filter(airline__pk=airline_id)
        return flights.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_arrival_flights(country_id: int) -> QuerySet[Flight]:
        """Get all flights arriving to a country in the next 12 hours

        Args:
            country_id (int): ID of the country

        Returns:
            QuerySet[Flight]: Collection of flights
        """
        query = Flight.objects.filter(destination_country__id=country_id)
        query = query.filter(arrival_datetime__gte=timezone.now())
        query = query.filter(arrival_datetime__lte=timezone.now() + timedelta(hours=12))
        return query.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_departure_flights(country_id: int) -> QuerySet[Flight]:
        """Get all flights leaving a country in the next 12 hours

        Args:
            country_id (int): ID of the country

        Returns:
            QuerySet[Flight]: Collection of flights
        """
        country = Country.objects.filter(pk=country_id).first()
        if not country:
            return None
        query = Flight.objects.filter(origin_country__id=country_id)
        query = query.filter(departure_datetime__gte=timezone.now())
        query = query.filter(departure_datetime__lte=timezone.now() + timedelta(hours=12))
        return query.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_tickets_by_customer(customer_id: int) -> QuerySet[Ticket]:
        """Fetches all tickets belonging to a customer

        Args:
            customer_id (int): Id of the customer

        Returns:
            QuerySet[Ticket]: Collection of tickets
        """
        tickets = Ticket.objects.filter(customer__id=customer_id)
        return tickets.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_airlines_by_country(country_id: int) -> QuerySet[AirlineCompany]:
        """Get all airlines in a certain country

        Args:
            country_id (int): The country's ID

        Returns:
            QuerySet[AirlineCompany]: A QuerySet of AirlineCompany objects
        """
        airlines = AirlineCompany.objects.filter(country__id=country_id)
        return airlines.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_origin(country_id: int) -> QuerySet[Flight]:
        """Get flights that take off from a certain country

        Args:
            country_id (int): ID of the country

        Returns:
            QuerySet[Flight]: A QuerySet of Flight objects
        """
        results = Flight.objects.filter(origin_country__id=country_id)
        return results.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_destination(country_id: int) -> QuerySet[Flight]:
        """Get flights that land in a certain country

        Args:
            country_id (int): ID of the country

        Returns:
            QuerySet[Flight]: A QuerySet of Flight objects
        """
        results = Flight.objects.filter(destination_country__id=country_id)
        return results.all()
    
    @staticmethod
    @log_action
    @accepts(Date)
    def get_flights_by_departure_date(date: Date) -> QuerySet[Flight]:
        """Get flights that depart on a certain date

        Args:
            date (Date): a date object to check on

        Returns:
            QuerySet[Flight]: QuerySet of Flight objects
        """
        flights = Flight.objects.filter(departure_datetime__date=date)
        return flights.all()
    
    @staticmethod
    @log_action
    @accepts(Date)
    def get_flights_by_arrival_date(date: Date) -> QuerySet[Flight]:
        """Get flights that arrive on a certain date

        Args:
            date (Date): a date object to check on

        Returns:
            QuerySet[Flight]: QuerySet of Flight objects
        """
        flights = Flight.objects.filter(arrival_datetime__date=date)
        return flights.all()
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_customer(customer_id: int) -> QuerySet[Flight]:
        """Fetch all flights for a customer

        Args:
            customer_id (int): ID of the customer

        Returns:
            QuerySet[Flight]: A QuerySet of Flight objects
        """
        flights = Flight.objects.filter(tickets__customer__id=customer_id)
        return flights.all()
