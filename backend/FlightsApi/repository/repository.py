# Python builtins
import logging
from datetime import timedelta
from datetime import date as Date

from typing import Union, Iterable, List, Dict, Tuple
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

logger = logging.getLogger('django')

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


class Repository():
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def get_by_id(dbtable: DBTables, id: int) -> dict:
        """
        Get item from a certain table by id.

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model.
            id (int): id of the row to get.

        Returns:
            dict: A dictionary of the row. Blank dictionary if not found.
        
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
    def get_or_create_group(name: str) -> dict:
        """
        Returns a dictionary of a group with the specified name, creates if doesn't exist.

        Args:
            name (str): A group name.

        Returns:
            Type[Dict]: A dictionary of the group.
        """
        # Get/create the group
        group, created = Group.objects.get_or_create(name=name)
        # Return a serialized instance
        return DBTables.GROUP.serializer(group).data
    
    @staticmethod
    @log_action
    @accepts(DBTables)
    def get_all(dbtable: DBTables, paginator: Paginate = Paginate()) -> List[dict]:
        """
        Get all rows from certain table

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            list[dict]: List of all serialized rows from model.
        """
        # Get the instances
        paginator.total = dbtable.model.objects.count()
        all_objects = dbtable.model.objects.all()[paginator.slice]
        # Serialize them
        result = [dbtable.serializer(obj).data for obj in all_objects]
        return result

    @staticmethod
    @log_action
    @accepts(DBTables)
    def add(dbtable: DBTables, **fields) -> Tuple[dict, bool]:
        """
        Creates and saves an item.

        Args:
            dbtable (DBTables): A DBTables objects corresponding with the right table/model.

        Returns:
            Tuple[dict, bool]: (Result, Success), 'Result' being a dictionary of the instance.
        """
        # Create the object
        deserialized_data = dbtable.serializer(data=fields)
        # Validate the data and return the result and a success/failure flag
        if deserialized_data.is_valid():
            deserialized_data.save()
            # If data is valid return a serialized instance of it
            return deserialized_data.data, True
        else:
            # If there were errors in the creation of the instance return them
            return deserialized_data.errors, False
    
    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def update(dbtable: DBTables, id: int, **updated_values) -> Tuple[dict, bool]:
        """
        Update row from table with new data.

        Args:
            dbtable (DBTables): Table to update a row in.
            id (int): id of row to update.
            updated_values (kwargs): Any updated values.
            
        Raises:
            FetchError for not found rows.
            
        Returns:
            Tuple[dict, bool]: Updated instance, success flag
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
    def add_all(dbtable: DBTables, new_rows: Iterable[dict]) -> Tuple[List[dict], List[dict]]:
        """
        Add all rows to database.

        Args:
            dbtable (DBTables): Table to add the rows to.
            new_rows (list): Model objects to add to the database.
        
        Returns:
            Tuple[List[dict], List[dict]]: A tuple of successfully added and failed additions.
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
    @accepts(DBTables, int)
    def get_by_user_id(dbtable: DBTables, user_id: int):
        if not dbtable in (DBTables.ADMIN, DBTables.AIRLINECOMPANY, DBTables.CUSTOMER, DBTables.USER):
            return {}
        profile = dbtable.model.objects.filter(user__id=user_id).first()
        if profile:
            return dbtable.serializer(instance=profile).data
        else:
            return {}
            
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
            Tuple[dict, bool]: A tuple of a result, success.
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
    def get_user_by_username(username: str) -> Tuple[dict, bool]:
        """
        Get a user from its username.

        Args:
            username (str): A username to search for.

        Returns:
            Tuple[dict, bool]: A tuple of a result, success.
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
    @accepts((int, type(None)), (int, type(None)), (Date, type(None)), (int, type(None)), bool)
    def get_flights_by_parameters(origin_country_id: Union[int, None], destination_country_id: Union[int, None], date: Union[Date, None], airline_id: Union[int, None], allow_cancelled: bool, paginator: Paginate = Paginate()) -> List[dict]:
        """
        Returns a list of flights that fit the parameters.

        Args:
            origin_country_id (int - Optional): id field of the origin country. If None ignores this while filtering.
            destination_country_id (int - Optional): id field of the destination country. If None ignores this while filtering.
            date (date - Optional): date of departure. If None ignores this while filtering.
            airline_id (int - Optional): id field of the operating airline. If None ignores this while filtering.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A list of dictionaries of flights.
        """
        query = Flight.objects.all()
        if origin_country_id:
            # Get all flights that take off from origin_country
            query = query.filter(origin_country__id=origin_country_id)
        if destination_country_id:
            # Of those flights, get the ones that go to destination_country
            query = query.filter(destination_country__id = destination_country_id)
        if date:
            # Of those flights get any that depart on the specified date
            query = query.filter(departure_datetime__date = date)
        if airline_id:
            # Of those flights get those that are operated by the specified airline
            query = query.filter(airline__id = airline_id)        
        if not allow_cancelled:
            query = query.filter(is_cancelled=False)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_airline_id(airline_id: int, paginator: Paginate) -> List[dict]:
        """
        Returns a list of flights that are owned by the specified airline.
        
        Args:
            airline_id (int): An airline ID.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            list[dict]: A list of dictionaries of flights.
        """
        # Create the query
        query = Flight.objects.filter(airline__pk=airline_id)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_arrival_flights(country_id: int, paginator: Paginate) -> List[dict]:
        """
        Get all flights arriving to a country in the next 12 hours.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A list of dictionaries of flights.
        """
        # Create a query
        query = Flight.objects.filter(destination_country__id=country_id)
        query = query.filter(arrival_datetime__gte=timezone.now())
        query = query.filter(arrival_datetime__lte=timezone.now() + timedelta(hours=12))
        
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_departure_flights(country_id: int, paginator: Paginate) -> List[dict]:
        """
        Get all flights leaving a country in the next 12 hours.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A list of dictionaries of flights.
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
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_tickets_by_customer(customer_id: int, paginator: Paginate) -> List[dict]:
        """
        Fetches all tickets belonging to a customer.

        Args:
            customer_id (int): Id of the customer.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A list of dictionaries of tickets.
        """
        # Create the query
        query = Ticket.objects.filter(customer__id=customer_id)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        tickets = [DBTables.TICKET.serializer(ticket).data for ticket in query]
        return tickets
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_airlines_by_country(country_id: int, paginator: Paginate) -> List[dict]:
        """
        Get all airlines in a certain country.

        Args:
            country_id (int): The country's ID.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A List of airline dictionaries.
        """
        # Create the query
        query = AirlineCompany.objects.filter(country__id=country_id)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        airlines = [DBTables.AIRLINECOMPANY.serializer(airline).data for airline in query]
        return airlines
    
    @staticmethod
    @log_action
    @accepts(str)
    def get_airlines_by_name(name: str,  paginator: Paginate, allow_deactivated = False) -> List[dict]:
        """
        Get all airlines whos name contains a str.

        Args:
            name (str): A search string.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A List of airline dictionaries.
        """
        # Create the query
        query = AirlineCompany.objects.filter(name__icontains=name)
        
        # If deactivated are not allowed filter to only active
        if not allow_deactivated:
            query = query.filter(user__is_active=True)
        
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialized the results
        airlines = [DBTables.AIRLINECOMPANY.serializer(airline).data for airline in query]
        return airlines
    
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_origin(country_id: int, paginator: Paginate) -> List[dict]:
        """Get flights that take off from a certain country.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(origin_country__id=country_id)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_destination(country_id: int, paginator: Paginate) -> List[dict]:
        """Get flights that land in a certain country.

        Args:
            country_id (int): ID of the country.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(destination_country__id=country_id)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(Date)
    def get_flights_by_departure_date(date: Date, paginator: Paginate) -> List[dict]:
        """Get flights that depart on a certain date.

        Args:
            date (Date): a date object to check on.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(departure_datetime__date=date)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(Date)
    def get_flights_by_arrival_date(date: Date, paginator: Paginate) -> List[dict]:
        """Get flights that arrive on a certain date.

        Args:
            date (Date): a date object to check on.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(arrival_datetime__date=date)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights
    
    @staticmethod
    @log_action
    @accepts(int)
    def get_flights_by_customer(customer_id: int, paginator: Paginate) -> List[dict]:
        """Fetch all flights for a customer.

        Args:
            customer_id (int): ID of the customer.
            paginator (Paginate - Optional): A Paginate object if required.

        Returns:
            List[dict]: A List of flight dictionaries.
        """
        # Create the query
        query = Flight.objects.filter(tickets__customer__id=customer_id)
        # Paginate the results
        paginator.total = query.count()
        query = query.all()[paginator.slice]
        # Serialize the results
        flights = [DBTables.FLIGHT.serializer(flight).data for flight in query]
        return flights

    @staticmethod
    @log_action
    @accepts(int)
    def get_tickets_by_flight(flight_id: int):
        """Get all tickets from a flight

        Args:
            flight_id (int): Flight ID

        Returns:
            list[dict]: A list of all tickets
        """
        query = Ticket.objects.filter(flight__id=flight_id).all()
        tickets = [DBTables.TICKET.serializer(ticket).data for ticket in query]
        return tickets
        

    @staticmethod
    @log_action
    @accepts(DBTables, int)
    def instance_exists(dbtable: DBTables, id: int) -> bool:
        """Check if an instance exists

        Args:
            dbtable (DBTables): A database table to check
            id (int): An id to check for instance

        Returns:
            bool: True if exsits, False otherwise
        """
        exists = dbtable.model.objects.filter(pk=id).exists()
        return exists
    
    @staticmethod
    @accepts(int, int)
    def is_flight_bookable(id: int, seat_count: int = 1) -> Tuple[bool, str]:
        """Checks if it's possible to book a certain amount of seats on a specific flight.

        Args:
            id (int): id of the flight
            seat_count (int, optional): Amount of seats wanted for booking. Defaults to 1.

        Returns:
            Tuple[bool, str]: A Tuple of Bookable(bool), Reason(str)
        """
        flight_exists = Repository.instance_exists(DBTables.FLIGHT, id)
        if not flight_exists:
            return False, 'the flight does not exist'
        
        flight = Flight.objects.get(pk=id)
        if flight.is_cancelled:
            return False, 'the flight was cancelled'
        
        flight_happened = flight.departure_datetime <= timezone.now()
        if flight_happened:
            return False, 'the flight has already taken off'
        
        all_tickets = Repository.get_tickets_by_flight(id)
        total_booked_seats = 0
        # Count how many seats were booked
        for ticket in all_tickets:
            total_booked_seats +=  0 if ticket['is_cancelled'] else ticket['seat_count']
        # Check if there are enough seats to fulfill this order
        if total_booked_seats + seat_count > flight.total_seats:
            return False, f'the flight only has {flight.total_seats - total_booked_seats} seat(s) left'
        
        return True, 'the flight can be booked'
    
    @staticmethod
    @accepts(DBTables)
    def get_users_by_usertype(usertype: DBTables) -> List[dict]:
        if not usertype in (DBTables.ADMIN, DBTables.AIRLINECOMPANY, DBTables.CUSTOMER):
            raise ValueError("User type must be one of the following: ADMIN, AIRLINECOMPANY, CUSTOMER")
        # Get the users
        
        match (usertype):
            case DBTables.ADMIN:
                users = User.objects.filter(groups__name="admin")
                users = [DBTables.USER.serializer(user).data for user in users]
                for user in users:
                    admin = Admin.objects.filter(user__id=user['id']).first()
                    user['admin'] = DBTables.ADMIN.serializer(admin).data if admin else None
                    
            case DBTables.AIRLINECOMPANY:
                users = User.objects.filter(groups__name="airline")
                users = [DBTables.USER.serializer(user).data for user in users]
                for user in users:
                    airline = AirlineCompany.objects.filter(user__id=user['id']).first()
                    user['airline'] = DBTables.AIRLINECOMPANY.serializer(airline).data if airline else None

            case DBTables.CUSTOMER:
                users = User.objects.filter(groups__name="customer")
                users = [DBTables.USER.serializer(user).data for user in users]
                for user in users:
                    customer = Customer.objects.filter(user__id=user['id']).first()
                    user['customer'] = DBTables.CUSTOMER.serializer(customer).data if customer else None
            case other:
                raise ValueError("User type must be one of the following: ADMIN, AIRLINECOMPANY, CUSTOMER")
        
        # Serialize the users
        return users
    
    
    @staticmethod
    @accepts(int, str)
    def assign_group_to_user(user_id: int, group_name: str) -> dict:
        """Adds a user to a specific group.

        Args:
            user_id (int): ID of the user
            group_name (str): Name of the group to add the user to

        Raises:
            EntityNotFoundException: If the user was not found.
            UserAlreadyInGroupException: If the user is already in a group.

        Returns:
            dict: A serialized user dictionary after addition to the group.
        """
        # Get and check the user by ID
        user = User.objects.filter(pk=user_id).first()
        if not user:
            raise EntityNotFoundException('This user does not exist.')
        
        # Check if the user is already in a group
        if len(user.groups.all()) > 0:
            raise UserAlreadyInGroupException()
        
        # Add the user to a group or remove from all groups if group_name is blank
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            group.user_set.add(user)
        else:
            user.groups.clear()
        user.save()
        
        return DBTables.USER.serializer(user).data

    @staticmethod
    @accepts(User)
    def serialize_user(user: User) -> dict:
        """Takes a User object and serializes it

        Args:
            user (User): A User object to serialize

        Returns:
            dict: A serialized User
        """
        return DBTables.USER.serializer(user).data

    # @staticmethod
    # @log_action
    # def authenticate(request, username: str, password: str):
    #     user = authenticate(request, username=username, password=password)
    #     if user:
    #         return DBTables.USER.serializer(user).data
    #     else:
    #         return {}
        
    # def is_authenticated(user_id):
    #     user = Repository.get_by_id(DBTables.USER, user_id)
    #     return user.is_authenticated()