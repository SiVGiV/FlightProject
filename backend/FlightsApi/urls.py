from django.urls import path
from .views import *

urlpatterns = [
    path('logout/', LogoutView.as_view(), name="logout"),
    path('login/', LoginView.as_view(), name="login"),
    path('whoami/', WhoAmIView.as_view(), name="whoami"),
    path('csrf/', CSRFTokenView.as_view(), name="csrf"),
    
    path('users/<str:usertype>/', UsersView.as_view(), name="users"),
        
    path('admins/', AdminsView.as_view(), name="admins"),
    path('admin/<int:id>/', AdminView.as_view(), name="admin"),
    
    path('airlines/', AirlinesView.as_view(), name="airlines"),
    path('airline/<int:id>/', AirlineView.as_view(), name="airline"),
    
    path('countries/', CountriesView.as_view(), name="countries"),
    path('country/<int:id>/', CountryView.as_view(), name="country"),
    
    path('customers/', CustomersView.as_view(), name="customers"),
    path('customer/<int:id>/', CustomerView.as_view(), name="customer"),
    
    path('flights/', FlightsView.as_view(), name="flights"),
    path('flight/<int:id>/', FlightView.as_view(), name="flight"),
    
    path('tickets/', TicketsView.as_view(), name="tickets"),
    path('ticket/<int:id>/', TicketView.as_view(), name="ticket"),
]
