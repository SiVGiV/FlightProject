from rest_framework import serializers
from ..models import Country, User, Admin, AirlineCompany, Customer, Flight, Ticket
from django.contrib.auth.models import Group


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"

        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']

        
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = "__all__"

        
class AirlineCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = AirlineCompany
        fields = "__all__"
        # fields = ['name', 'country_id', 'user_id']

        
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        # fields = ['first_name', 'last_name', 'address', 'phone_number', 'user_id']

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"
        # fields = [
        #     'airline_id',
        #     'origin_country_id', 
        #     'destination_country_id', 
        #     'departure_datetime', 
        #     'arrival_datetime', 
        #     'total_seats', 
        #     'is_canceled'
        # ]


        
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"
        # fields = [
        #     'flight_id',
        #     'customer_id',
        #     'seat_count',
        #     'is_canceled'
        # ]

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"