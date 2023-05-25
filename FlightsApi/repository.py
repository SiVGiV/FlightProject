from models import models, Country, UserRole, User, Admin,\
                   AirlineCompany, Customer, Flight, Ticket
from datetime import datetime, timedelta
import logging
logger = logging.getLogger()
class Repository():
    @staticmethod
    def get_by_id(model: type[models.Model], id: int):
        # TODO test existing id
        # TODO test nonexisting id
        # TODO test non-existing model
        """Get item of type model by id

        Args:
            model (type[Model]): Model to get row from
            id (int): id of the row to get

        Returns:
            Model object: An item or None if not found
        """
        return model.objects.filter(pk=id).first()
    
    @staticmethod
    def get_all(model: type[models.Model]):
        # TODO test model
        # TODO test different obj
        """Get all rows from certain model

        Args:
            model (type[Model]): The model to fetch rows from

        Returns:
            list: All rows from model
        """
        return model.objects.all()
        
    @staticmethod
    def add(new_obj):
        # TODO test missing fields
        # TODO test wrong value types
        # TODO test correct data
        """Saves a new row to a model

        Args:
            new_row (obj): A new object of the model's type
        """
        # Verify that the save method actually exists in the object
        if not hasattr(new_obj, 'save'):
            logger.error("Passed non-model object.")
        elif not callable(new_obj.save):
            logger.error("new_obj.save is not callable - is this the right object?")
        else:
            new_obj.save()
    
    @staticmethod
    def update(model: type[models.Model], id: int, **updated_values):
        # TODO test non existing fields
        # TODO test wrong value types
        # TODO test correct data
        """Update row from model with new data

        Args:
            model (type[Model]): Model to update a row in
            id (int): id of row to update
        KeywordArgs:
            Any updated values
        """
        item = Repository.get_by_id(model, id)
        for key, value in updated_values.items():
            if hasattr(item, key):
                setattr(item, key, value)
            else:
                logger.warning("Attempted to edit a non existing attribute '%s'." % key)
        item.save()
    
    @staticmethod
    def add_all(new_rows: list[type[models.Model]]):
        # TODO test bad types in list
        # TODO test good insert
        """Add all rows to database

        Args:
            new_rows (list): Model objects to add to the database
        """
        for row in new_rows:
            if not hasattr(row, 'save'):
                continue
            elif not callable(row.save):
                continue
            row.save()
    
    @staticmethod
    def remove(model, id: int):
        # TODO test nonexisting id
        # TODO test successful removal
        """Remove a row from the database

        Args:
            model (Model): the model to remove from
            id (int): The id of the row to remove
        """
        item_to_remove = Repository.get_by_id(model, id)
        if item_to_remove:
            item_to_remove.delete()
    
    @staticmethod
    def get_airline_by_username(username: str):
        airline = AirlineCompany.objects.get(user__username=username)
        return airline
    
    @staticmethod
    def get_customer_by_username(username: str):
        customer = Customer.objects.get(user__username=username)
        return customer
    
    @staticmethod
    def get_user_by_username(username: str):
        user = User.objects.get(username=username)
        return user
    
    @staticmethod
    def get_flights_by_parameters(origin_country_id: int, destination_country_id: int, date: datetime.date):
        query = Flight.objects.filter(origin_country__id=origin_country_id)
        query = query.filter(destination_country__id = destination_country_id)
        query = query.filter(departure_datetime__date = date)
        return query
    
    @staticmethod
    def get_flights_by_airline_id(airline_id: int):
        flights = Flight.objects.filter(airline__pk=airline_id)
        return flights
    
    @staticmethod
    def get_arrival_flights(country_id: int):
        country = Country.objects.get(pk=country_id)
        if not country:
            return None
        query = Flight.objects.filter(destination_country__id=country_id)
        query = query.filter(arrival_datetime__gte=datetime.now())
        query = query.filter(arrival_datetime__lte=datetime.now() + timedelta(hours=12))
        return query
    
    @staticmethod
    def get_departure_flights(country_id: int):
        country = Country.objects.get(pk=country_id)
        if not country:
            return None
        query = Flight.objects.filter(origin_country__id=country_id)
        query = query.filter(departure_datetime__gte=datetime.now())
        query = query.filter(departure_datetime__lte=datetime.now() + timedelta(hours=12))
        return query
    
    @staticmethod
    def get_tickets_by_customer(customer_id: int):
        tickets = Ticket.objects.filter(customer__id=customer_id)
        return tickets
    
    @staticmethod
    def get_airlines_by_country(country_id: int):
        country = Repository.get_by_id(Country, country_id)
        return country.airlines
    
    @staticmethod
    def get_flights_by_origin(country_id: int):
        country = Repository.get_by_id(Country, country_id)
        return country.origin_flights
    
    @staticmethod
    def get_flights_by_destination(country_id: int):
        country = Repository.get_by_id(Country, country_id)
        return country.destination_flights
    
    @staticmethod
    def get_flights_by_departure_date(date: datetime.date):
        flights = Flight.objects.filter(departure_datetime__date=date)
        return flights
    
    @staticmethod
    def get_flights_by_arrival_date(date: datetime.date):
        flights = Flight.objects.filter(arrival_datetime__date=date)
        return flights
    
    @staticmethod
    def get_flights_by_customer(customer_id: int):
        query = Ticket.objects.filter(customer__id=customer_id)
        flights = []
        for ticket in query:
            flights.append(ticket.flight)
        return flights