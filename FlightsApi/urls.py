"""
URL configuration for FlightProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import *

urlpatterns = [
    path('logout/', logout, name="logout"),
    
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
