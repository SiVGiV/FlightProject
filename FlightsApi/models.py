from django.db import models
from django.contrib.auth.models import AbstractUser


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=2, unique=True)
    flag = models.CharField(max_length=200, unique=True)
                
    class Meta:
        verbose_name_plural = "Countries"
            
    def __repr__(self) -> str:
        return f"<{self.name}>"

    def __str__(self) -> str:
        return f"{self.name}"
    

class UserRole(models.Model):
    role_name = models.CharField(max_length=100, unique=True)
                        
    class Meta:
        verbose_name = "User Role"
            
    def __repr__(self) -> str:
        return f"<{self.role_name}>"

    def __str__(self) -> str:
        return f"{self.role_name}"


class User(AbstractUser):
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name='users', null=True, blank=True)


class Admin(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin', unique=True)
        
    def __repr__(self) -> str:
        return f"<Admin {self.first_name} {self.last_name}>"
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class AirlineCompany(models.Model):
    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='airline', unique=True)
            
    class Meta:
        verbose_name = "Airline Company"
        verbose_name_plural = "Airline Companies"
            
    def __repr__(self) -> str:
        return f"<AirlineCompany {self.name}>"
    
    def __str__(self) -> str:
        return self.name
    

class Customer(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200, unique=True)
    credit_card_number = models.CharField(max_length=200, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', unique=True)
    
    def __repr__(self) -> str:
        return f"<Customer {self.first_name} {self.last_name}>"
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
    

class Flight(models.Model):
    airline = models.ForeignKey(AirlineCompany, on_delete=models.CASCADE, related_name='flights')
    origin_country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='origin_flights')
    destination_country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='destination_flights')
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()
    remaining_seats = models.IntegerField()
    
    def __repr__(self) -> str:
        return f"<Flight #{self.pk}: {self.origin_country}->{self.destination_country} @ {self.departure_datetime}>"
    
    def __str__(self) -> str:
        return f"Flight #{self.pk}"
    

class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='tickets')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets')
    seat_count = models.IntegerField()

    class Meta:
        unique_together = ('flight', 'customer',)