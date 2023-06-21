# Python builtins
import logging
from datetime import timedelta
from datetime import date as Date
from typing import Type, Iterable, Union, List, Dict, Tuple
from enum import Enum, unique

# Django imports
from django.db.models import Model, QuerySet
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone

# [L] Models
from ..models import Country, User,\
                    Admin, AirlineCompany, Customer, \
                    Flight, Ticket

# [L] Repository
from .serializers import CountrySerializer, UserSerializer,\
                        AdminSerializer, AirlineCompanySerializer, CustomerSerializer, \
                        FlightSerializer, TicketSerializer, GroupSerializer
from .errors import *

# [L] Utilities
from ..utils import accepts, log_action

@unique
class DBTables(Enum):
    """
    A Class representing a table in the repository:
    
    Country=0, User=1, Group=2, Admin=3, AirlineCompany=4, Customer=5, Flight=6, Ticket=7
    """
    COUNTRY = 0
    USER = 1
    GROUP = 2
    ADMIN = 3
    AIRLINECOMPANY = 4
    CUSTOMER = 5
    FLIGHT = 6
    TICKET = 7
    
    @property
    def model(self):
        match (self.value):
            case DBTables.COUNTRY.value:
                return Country
            case DBTables.USER.value:
                return User
            case DBTables.GROUP.value:
                return Group
            case DBTables.ADMIN.value:
                return Admin
            case DBTables.AIRLINECOMPANY.value:
                return AirlineCompany
            case DBTables.CUSTOMER.value:
                return Customer
            case DBTables.FLIGHT.value:
                return Flight
            case DBTables.TICKET.value:
                return Ticket
            case other:
                message = f"Model could not be found for {self.name}."
                logger.error(message)
                raise NotFoundModelOrSerializerException(message)
            
    @property
    def serializer(self):
        match (self.value):
            case DBTables.COUNTRY.value:
                return CountrySerializer
            case DBTables.USER.value:
                return UserSerializer
            case DBTables.GROUP.value:
                return GroupSerializer
            case DBTables.ADMIN.value:
                return AdminSerializer
            case DBTables.AIRLINECOMPANY.value:
                return AirlineCompanySerializer
            case DBTables.CUSTOMER.value:
                return CustomerSerializer
            case DBTables.FLIGHT.value:
                return FlightSerializer
            case DBTables.TICKET.value:
                return TicketSerializer
            case other:
                message = f"Serializer could not be found for {self.name}."
                logger.error(message)
                raise NotFoundModelOrSerializerException(message)
    
    @staticmethod
    @accepts(str)
    def from_string(input: str):
        if input.isdecimal():
            try:
                return DBTables(int(input))
            except ValueError:
                message = f"No table found with the value '{input}'."
                logger.error(message, exc_info=True)
                raise DBTAbleDoesNotExistException(message)
        elif input.isascii() and input.isalpha():
            try:
                return DBTables[input.upper()]
            except (ValueError, KeyError):
                message = f"No table found named '{input}'."
                logger.error(message, exc_info=True)
                raise DBTAbleDoesNotExistException(message)
        else:
            message = f"Cannot convert '{input}' to a DBTables object."
            logger.warning(message)
            raise UnacceptableInput(message)


logger = logging.getLogger()

class Repository():
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def get_by_id(dbtable: DBTables, id: int) -> Union[Model, None]:
        """Get item of type model by id

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model
            id (int): id of the row to get

        Returns:
            Dict: A serialized dictionary of the row
        
        Raises:
            OutOfBoundsException for bad ID values
        """
        # Validate arguments
        if id <= 0:
            raise OutOfBoundsException("ID must be larger than 0.")
        
        # Get and return item by id
        query = dbtable.model.objects.filter(pk=id).first()
        if query:
            result = dbtable.serializer(query).data
            if result:
                return result
        return {}

    @staticmethod
    @log_action
    @accepts(str)
    def get_or_create_group(name: str): # DOCME Docstring
        group = Group.objects.get_or_create(name=name)
        return DBTables.GROUP.serializer(group).data
    
    @staticmethod
    @log_action
    @accepts(DBTables)
    def get_all(dbtable: DBTables) -> List[Dict]:
        """Get all rows from certain table

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model


        Returns:
            list[dict]: List of all serialized rows from model
        """
        all_objects = dbtable.model.objects.all()
        result = [dbtable.serializer(obj).data for obj in all_objects]
        return result

    @staticmethod
    @log_action
    @accepts(DBTables)
    def add(dbtable: DBTables, **fields) -> Tuple[Dict, bool]: # DOCME
        """Creates and saves an object

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model

        Returns:
            Tuple[Dict, bool]: (Result, Success), 'Result' being a dictionary of the instance
        """
        # Try creating the object - expects failure if a field has a mismatching type or value
        deserialized_data = dbtable.serializer(data=fields)
        if deserialized_data.is_valid():
            new_obj = deserialized_data.save()
            return dbtable.serializer(new_obj).data, True
        else:
            errors = deserialized_data.errors
            return errors, False
    
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def update(dbtable: DBTables, id: int, **updated_values) -> Dict: # DOCME
        """Update row from model with new data

        Args:
            model (DBTables): Model to update a row in
            id (int): id of row to update
        KWArgs:
            Any updated values
        Raises:
            UpdateError for non existing attributes, bad attribute types
            FetchError for not found rows
        """
        # Get the item
        instance = dbtable.model.objects.filter(id=id).first()
        if not instance:
            raise FetchError(f"Failed to find an instance of '{dbtable.name}' with ID #{id}")
        
        deserialized_data = dbtable.serializer(instance=instance, data=updated_values, partial=True)
        if deserialized_data.is_valid():
            new_obj = deserialized_data.save()
            return dbtable.serializer(new_obj).data, True
        else:
            errors = deserialized_data.errors
            return errors, False
    
    @staticmethod
    @log_action
    @accepts(DBTables)
    def add_all(dbtable: DBTables, entry_list: Iterable[Dict]) -> Tuple[List[Dict], List[Dict]]: # DOCME
        """Add all rows to database

        Args:
            model: Table to add the rows to
            new_rows (list): Model objects to add to the database
        
        Returns:
            list of Model objects that were added 
            It is recommended to check if the returned length is the same as the passed length
            # DOCME Add documentation for failed
        """
        created = []
        failed = []
        for fields in entry_list:
            new_instance = Repository.add(dbtable, **fields)
            if new_instance[1]:
                created.append(new_instance[0])
            else:
                failed.append((fields, new_instance[0]))
        # Return all created objects
        return created, failed
    
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def remove(dbtable: DBTables, id: int) -> bool: # DOCME
        """Remove a row from the database

        Args:
            model (Model): the model to remove from
            id (int): The id of the row to remove
        """
        # Get the item
        instance = dbtable.model.objects.filter(id=id).first()
            
        # If an item was found, delete it
        if instance:
            deleted = instance.delete()
            if deleted[0] > 0:
                return True
            else:
                return False
        else:
            return False
            
        
    @staticmethod
    @log_action
    @accepts(str)
    def get_airline_by_username(username: str) -> Tuple[Dict, bool]: # TESTME # DOCME
        """Get an AirlineCompany from its username

        Args:
            username (str): A username to search for

        Returns:
            AirlineCompany, None: An AirlineCompany object if found, otherwise None
        """
        airline = AirlineCompany.objects.filter(user__username=username).first()
        if airline:
            return DBTables.AIRLINECOMPANY.serializer(instance=airline).data, True
        else:
            return {}, False
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_customer_by_username(username: str) -> Union[Customer, None]: # TESTME # DOCME
        """Get a Customer from its username

        Args:
            username (str): A username to search for

        Returns:
            Customer, None: A Customer object if found, otherwise None
        """
        customer = Customer.objects.filter(user__username=username).first()
        if customer:
            return DBTables.CUSTOMER.serializer(instance=customer).data, True
        else:
            return {}, False
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_user_by_username(username: str) -> Union[User, None]: # TESTME # DOCME
        """Get a user from its username

        Args:
            username (str): A username to search for

        Returns:
            User: A User model object (or None)
        """
        user = User.objects.filter(username=username).first()
        if user:
            return DBTables.USER.serializer(instance=user).data, True
        else:
            return {}, False
    
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
        # Finally, of those flights get any that depart on the specified date
        query = query.filter(departure_datetime__date = date)
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        query = Flight.objects.filter(airline__pk=airline_id)
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        query = Ticket.objects.filter(customer__id=customer_id)
        
        tickets = [DBTables.TICKET.serializer(ticket).data for ticket in query.all()]
        return tickets
    
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
        query = AirlineCompany.objects.filter(country__id=country_id)
        
        airlines = [DBTables.AIRLINECOMPANY.serializer(airline).data for airline in query.all()]
        return airlines
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_airlines_by_name(name: str) -> QuerySet[AirlineCompany]:
        """Get all airlines whos name contains a str

        Args:
            name (str): A search string

        Returns:
            QuerySet[AirlineCompany]: A QuerySet of AirlineCompany objects
        """
        query = AirlineCompany.objects.filter(name__icontains=name)
        
        airlines = [DBTables.AIRLINECOMPANY.serializer(airline).data for airline in query.all()]
        return airlines
    
    
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
        query = Flight.objects.filter(origin_country__id=country_id)
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        query = Flight.objects.filter(destination_country__id=country_id)
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        query = Flight.objects.filter(departure_datetime__date=date)
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        query = Flight.objects.filter(arrival_datetime__date=date)
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
    
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
        query = Flight.objects.filter(tickets__customer__id=customer_id)
        
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query.all()]
        return flights
