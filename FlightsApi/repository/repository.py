from django.db import models
from django.core.exceptions import ValidationError

from ..models import Country, User,\
                   AirlineCompany, Customer, Flight, Ticket
from .errors import *
                   
from datetime import datetime, timedelta
import logging

from typing import Type
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
        if not isclass(args[0]):
            raise WrongModelType("model must be of type Model")
        if not issubclass(args[0], models.Model):
            raise WrongModelType("model must be of type Model")
        return func(*args, **kwargs)
    return wrapper


class Repository():
    @staticmethod
    @verify_model
    def get_by_id(model: Type[models.Model], id: int):
        """Get item of type model by id

        Args:
            model (type[models.Model]): Model to get row from
            id (int): id of the row to get

        Returns:
            Model object: An item or None if not found
        
        Raises:
            FetchError for bad ID values
        """
        if not isinstance(id, int):
            raise FetchError("id must be an integer")
        if id < 0:
            raise FetchError("id must be larger or equal to 0")
        return model.objects.filter(pk=id).first()
    
    @staticmethod
    @verify_model
    def get_all(model: Type[models.Model]):
        """Get all rows from certain model

        Args:
            model (type[Model]): The model to fetch rows from

        Returns:
            list: All rows from model
        """
        return model.objects.all()
        
    @staticmethod
    @verify_model
    def add(model: Type[models.Model], **fields):
        """Saves a new row to a model

        Args:
            new_row (obj): A new object of the model's type
        
        Returns:
            obj of Model
            
        Raises:
            CreationError
        """
        try:
            # Use the User .create_user function for creating users (hashes passwords)
            if model == User:
                new_obj = model.objects.create_user(**fields)
            else:
                new_obj = model.objects.create(**fields)
        except (ValueError, TypeError) as e:
            raise CreationError(e)
        else:
            new_obj.save()
        return new_obj
        
    
    @staticmethod
    @verify_model
    def update(model: Type[models.Model], id: int, **updated_values):
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
        item = Repository.get_by_id(model, id)
        if not item:
            raise FetchError("Failed to find an item of model with ID #%i" % id)
        for field, value in updated_values.items():
            if hasattr(item, field):
                    setattr(item, field, value)
            else:
                raise UpdateError("Attempted to edit a non existing attribute '%s'." % field)
        try:
            item.save()
        except (ValueError, TypeError, ValidationError) as e:
            raise UpdateError("Attempted to set attribute to bad data type/value", e)
        return item
    
    @staticmethod
    @verify_model
    def add_all(model: Type[models.Model], entry_list: list[dict]):
        """Add all rows to database

        Args:
            model: 
            new_rows (list): Model objects to add to the database
        """
        returns = []
        for fields in entry_list:
            returns.append(Repository.add(model, **fields))
        return returns
    
    @staticmethod
    @verify_model
    def remove(model, id: int):
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

