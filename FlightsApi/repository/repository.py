# Python builtins
import logging
from datetime import timedelta
from datetime import date as Date

from typing import Type, Iterable, List, Dict, Tuple
from enum import Enum, unique

# Django imports
from django.contrib.auth.models import Group
from django.utils import timezone

# [L] Models
from ..models import Country, User,\
                    Admin, AirlineCompany, Customer, \
                    Flight, Ticket
from .serializers import CountrySerializer, UserSerializer,\
                        AdminSerializer, AirlineCompanySerializer, CustomerSerializer, \
                        FlightSerializer, TicketSerializer, GroupSerializer

# [L] Repository
from .errors import *
from .repository_utils import Paginate

# [L] Utilities
from ..utils import accepts, log_action

logger = logging.getLogger()


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
        """
        Returns a DBTables object with the name specified.

        Args:
            input (str): A name of a table, or the value(index) of said table in string form.

        Raises:
            DBTAbleDoesNotExistException: If a table doesn't exist that matches the input.
            UnacceptableInput: If the input contains impossible characters or character combinations.

        Returns:
            Type[DBTables]: A DBTables object.
        """
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


class Repository():
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def get_by_id(dbtable: DBTables, id: int) -> Type[Dict]:
        """
        Get item from a certain table by id.

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model.
            id (int): id of the row to get.

        Returns:
            Dict: A dictionary of the row. Blank dictionary if not found.
        
        Raises:
            OutOfBoundsException for bad ID values.
        """
        # Validate arguments
        if id <= 0:
            raise OutOfBoundsException("ID must be larger than 0.")
        
        # Get and return item by id
        query = dbtable.model.objects.filter(pk=id).first()
        if query:
            result = dbtable.serializer(query).data
            if result:
                # If found an instance and serialized it return a serialized version of it
                return result
        # If not found an instance or failed to serialize it return an empty result
        return {}

    @staticmethod
    @log_action
    @accepts(str)
    def get_or_create_group(name: str) -> Type[Dict]:
        """
        Returns a dictionary of a group with the specified name, creates if doesn't exist.

        Args:
            name (str): A group name.

        Returns:
            Type[Dict]: A dictionary of the group.
        """
        # Get/create the group
        group = Group.objects.get_or_create(name=name)
        # Return a serialized instance
        return DBTables.GROUP.serializer(group).data
    
    @staticmethod
    @log_action
    @accepts(DBTables)
    def get_all(dbtable: DBTables, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Get all rows from certain table

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model.
            paginator (Paginate): A Paginate object if required.


        Returns:
            list[dict]: List of all serialized rows from model.
        """
        # Get the instances
        all_objects = dbtable.model.objects.all()[paginator.slice]
        # Serialize them
        result = [dbtable.serializer(obj).data for obj in all_objects]
        return result

    @staticmethod
    @log_action
    @accepts(DBTables)
    def add(dbtable: DBTables, **fields) -> Tuple[Dict, bool]:
        """
        Creates and saves an item.

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model.

        Returns:
            Tuple[Dict, bool]: (Result, Success), 'Result' being a dictionary of the instance.
        """
        # Create the object
        deserialized_data = dbtable.serializer(data=fields)
        # Validate the data and return the result and a success/failure flag
        if deserialized_data.is_valid():
            new_obj = deserialized_data.save()
            # If data is valid return a serialized instance of it
            return dbtable.serializer(new_obj).data, True
        else:
            errors = deserialized_data.errors
            # If there were errors in the creation of the instance return them
            return errors, False
    
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def update(dbtable: DBTables, id: int, **updated_values) -> Dict:
        """
        Update row from table with new data.

        Args:
            dbtable (DBTables): Table to update a row in.
            id (int): id of row to update.
        Kwargs:
            updated_values: Any updated values.
        Raises:
            FetchError for not found rows.
        """
        # Get the item
        instance = dbtable.model.objects.filter(id=id).first()
        if not instance:
            raise FetchError(f"Failed to find an instance of '{dbtable.name}' with ID #{id}")
        # Update the data
        deserialized_data = dbtable.serializer(instance=instance, data=updated_values, partial=True)
        # Validate the data and return the result and a success/failure flag
        if deserialized_data.is_valid():
            new_obj = deserialized_data.save()
            return dbtable.serializer(new_obj).data, True
        else:
            errors = deserialized_data.errors
            return errors, False
    
    @staticmethod
    @log_action
    @accepts(DBTables)
    def add_all(dbtable: DBTables, new_rows: Iterable[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Add all rows to database.

        Args:
            dbtable (DBTables): Table to add the rows to.
            new_rows (list): Model objects to add to the database.
        
        Returns:
            Tuple[List[Dict], List[Dict]]: A tuple of successfully added and failed additions.
        """
        created = []
        failed = []
        for fields in new_rows:
            # Add a new instance
            new_instance = Repository.add(dbtable, **fields)
            # Route the result to the right list
            if new_instance[1]:
                created.append(new_instance[0])
            else:
                failed.append((fields, new_instance[0]))
        # Return all created objects
        return created, failed
    
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def remove(dbtable: DBTables, id: int) -> bool:
        """
        Remove a row from the database.

        Args:
            dbtable (DBTables): the table to remove from.
            id (int): The id of the row to remove.
            
        Returns:
            bool: True if succeeded, otherwise false.
        """
        # Get the item
        instance = dbtable.model.objects.filter(id=id).first()
            
        if instance:
            # If an item was found, delete it
            deleted = instance.delete()
            if deleted[0] > 0:
                # If succeeded return True
                return True
        else:
            # If not found or failed return False
            return False
            
    @staticmethod
    @log_action
    @accepts(str)
    def get_airline_by_username(username: str) -> Tuple[Dict, bool]:
        """
        Get an AirlineCompany from its username.

        Args:
            username (str): A username to search for.

        Returns:
            Tuple[Dict, bool]: A tuple of a result, success.
        """
        # Fetch the airline
        airline = AirlineCompany.objects.filter(user__username=username).first()
        if airline:
            # If an airline was found return a serialized instance of it
            return DBTables.AIRLINECOMPANY.serializer(instance=airline).data, True
        else:
            # if not found return empty result
            return {}, False
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_customer_by_username(username: str) -> Tuple[Dict, bool]:
        """
        Get a Customer from its username.

        Args:
            username (str): A username to search for.

        Returns:
            Tuple[Dict, bool]: A tuple of a result, success.
        """
        # Fetch the customer
        customer = Customer.objects.filter(user__username=username).first()
        if customer:
            # If a customer was found return a serialized instance of it
            return DBTables.CUSTOMER.serializer(instance=customer).data, True
        else:
            # If not found return empty result
            return {}, False
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_user_by_username(username: str) -> Tuple[Dict, bool]:
        """
        Get a user from its username.

        Args:
            username (str): A username to search for.

        Returns:
            Tuple[Dict, bool]: A tuple of a result, success.
        """
        user = User.objects.filter(username=username).first()
        if user:
            # Return a serialized result if found user
            return DBTables.USER.serializer(instance=user).data, True
        else:
            # Return a blank result if not found
            return {}, False
    
    @staticmethod
    @log_action
    @accepts(int, int, Date)
    def get_flights_by_parameters(origin_country_id: int, destination_country_id: int, date: Date, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Returns a list of flights that fit the parameters.

        Args:
            origin_country_id (int): id field of the origin country.
            destination_country_id (int): id field of the destination country.
            date (date): date of departure.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A list of dictionaries of flights.
        """
        # Get all flights that take off from origin_country
        query = Flight.objects.filter(origin_country__id=origin_country_id)
        # Of those flights, get the ones that go to destination_country
        query = query.filter(destination_country__id = destination_country_id)
        # Finally, of those flights get any that depart on the specified date
        query = query.filter(departure_datetime__date = date)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_airline_id(airline_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Returns a list of flights that are owned by the specified airline.
        
        Args:
            airline_id (int): An airline ID.
            paginator (Paginate): A Paginate object if required.

        Returns:
            list[Dict]: A list of dictionaries of flights.
        """
        # Create the query
        query = Flight.objects.filter(airline__pk=airline_id)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_arrival_flights(country_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Get all flights arriving to a country in the next 12 hours.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A list of dictionaries of flights.
        """
        # Create a query
        query = Flight.objects.filter(destination_country__id=country_id)
        query = query.filter(arrival_datetime__gte=timezone.now())
        query = query.filter(arrival_datetime__lte=timezone.now() + timedelta(hours=12))
        
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_departure_flights(country_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Get all flights leaving a country in the next 12 hours.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A list of dictionaries of flights.
        """
        # Fetch the country
        country = Country.objects.filter(pk=country_id).first()
        if not country:
            return []
        # Create a query
        query = Flight.objects.filter(origin_country__id=country_id)
        query = query.filter(departure_datetime__gte=timezone.now())
        query = query.filter(departure_datetime__lte=timezone.now() + timedelta(hours=12))
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_tickets_by_customer(customer_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Fetches all tickets belonging to a customer.

        Args:
            customer_id (int): Id of the customer.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A list of dictionaries of tickets.
        """
        # Create the query
        query = Ticket.objects.filter(customer__id=customer_id)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        tickets = [DBTables.TICKET.serializer(ticket).data for ticket in query]
        return tickets
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_airlines_by_country(country_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Get all airlines in a certain country.

        Args:
            country_id (int): The country's ID.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A List of airline dictionaries.
        """
        # Create the query
        query = AirlineCompany.objects.filter(country__id=country_id)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        airlines = [DBTables.AIRLINECOMPANY.serializer(airline).data for airline in query]
        return airlines
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_airlines_by_name(name: str, paginator: Paginate = Paginate()) -> List[Dict]:
        """
        Get all airlines whos name contains a str.

        Args:
            name (str): A search string.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A List of airline dictionaries.
        """
        # Create the query
        query = Dict.objects.filter(name__icontains=name)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialized the results
        airlines = [DBTables.AIRLINECOMPANY.serializer(airline).data for airline in query]
        return airlines
    
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_origin(country_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """Get flights that take off from a certain country.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(origin_country__id=country_id)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_destination(country_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """Get flights that land in a certain country.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(destination_country__id=country_id)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(Date)
    def get_flights_by_departure_date(date: Date, paginator: Paginate = Paginate()) -> List[Dict]:
        """Get flights that depart on a certain date.

        Args:
            date (Date): a date object to check on.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(departure_datetime__date=date)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(Date)
    def get_flights_by_arrival_date(date: Date, paginator: Paginate = Paginate()) -> List[Dict]:
        """Get flights that arrive on a certain date.

        Args:
            date (Date): a date object to check on.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(arrival_datetime__date=date)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_customer(customer_id: int, paginator: Paginate = Paginate()) -> List[Dict]:
        """Fetch all flights for a customer.

        Args:
            customer_id (int): ID of the customer.
            paginator (Paginate): A Paginate object if required.

        Returns:
            List[Dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(tickets__customer__id=customer_id)
        # Paginate the results
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
