import os
import json
import requests
import click
from requests.auth import HTTPBasicAuth
from random import randint, randrange
from randomuser import RandomUser
from datetime import datetime, timedelta
from FlightProject.settings import BASE_DIR

BASE_URL = "http://127.0.0.1:8000/api/"


SUPERUSER_USERNAME = os.environ['DJANGO_SUPERUSER_USERNAME']
SUPERUSER_PASSWORD = os.environ['DJANGO_SUPERUSER_PASSWORD']


def random_datetime(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

randcountry = lambda: randint(1, 194)
randdate = lambda: random_datetime(datetime.now(), datetime.now() + timedelta(weeks=156))
randdelta = lambda: timedelta(days=randint(0,1), hours=randint(0, 23), minutes=randint(0, 59))

@click.command()
@click.option('--admins', default=0, help='Number of admins to generate.', prompt=True, show_default=("(Default: 0)"))
@click.option('--airlines', default=0, help='Number of airlines to generate.', prompt=True, show_default=("(Default: 0)"))
@click.option('--customers', default=0, help='Number of customers to generate.', prompt=True, show_default=("(Default: 0)"))
@click.option('--flights', default=0, help='Number of flights to generate per airline.', prompt=True, show_default=("(Default: 0)"))
@click.option('--tickets', default=0, help='Number of tickets to generate per flight.', prompt=True, show_default=("(Default: 0)"))
def generate_data(admins, airlines, customers, flights, tickets):
    # Create admins
    admins_list = []
    auth = HTTPBasicAuth(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
    OUTPUT_FILE = BASE_DIR / "exposed/generated_data/output.json"
    print(f"Output file is '{ OUTPUT_FILE }'.")

    for index in range(admins):
        user = RandomUser()
        password = user.get_password()
        request_body = {
            'username': user.get_username(),
            'password': password,
            'email': user.get_email(),
            'first_name': user.get_first_name(),
            'last_name': user.get_last_name()
        }
        response = requests.post(BASE_URL + "admins/", data=request_body, auth=auth)
        if response.status_code == 201:
            admins_list.append(response.json()['data'])
            admins_list[index]['user']['password'] = password
            print(f'Created admin {index + 1}/{admins}...')
        else:
            print(response.json())
            
    # Create airlines
    airlines_list = []
    auth = HTTPBasicAuth(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)
    
    for index in range(airlines):
        user = RandomUser()
        password = user.get_password()
        request_body = {
            'username': user.get_username(),
            'password': password,
            'email': user.get_email(),
            'name': user.get_full_name() + ' Airlines',
            'country': randcountry()
        }
        response = requests.post(BASE_URL + "airlines/", data=request_body, auth=auth)
        if response.status_code == 201:
            airlines_list.append(response.json()['data'])
            airlines_list[index]['user']['password'] = password
            print(f'Created airline {index + 1}/{airlines}...')
        else:
            print(response.json())
            
    # Create customers
    customers_list = []
    auth = HTTPBasicAuth(SUPERUSER_USERNAME, SUPERUSER_PASSWORD)

    for index in range(customers):
        user = RandomUser()
        password = user.get_password()
        request_body = {
            'username': user.get_username(),
            'password': password,
            'email': user.get_email(),
            'first_name': user.get_first_name(),
            'last_name': user.get_last_name(),
            'address': user.get_street() + ', ' + user.get_city(),
            'phone_number': user.get_phone()
        }
        response = requests.post(BASE_URL + "customers/", data=request_body, auth=auth)
        if response.status_code == 201:
            customers_list.append(response.json()['data'])
            customers_list[index]['user']['password'] = password
            print(f'Created customer {index + 1}/{customers}...')
        else:
            print(response.json())

    # Create flights
    flight_dict = {}
    flight_index = 1
    total_flights = len(airlines_list) * flights
    for airline in airlines_list:
        flights_list = []
        auth = HTTPBasicAuth(airline['user']['username'], airline['user']['password'])

        for index in range(flights):
            date = randdate()
            request_body = {
                'origin_country': randcountry(),
                'destination_country': randcountry(),
                'departure_datetime': date.isoformat(),
                'arrival_datetime': (date + randdelta()).isoformat(),
                'total_seats': randint(50, 300)
            }
            
            response = requests.post(BASE_URL + "flights/", data=request_body, auth=auth)
            if response.status_code == 201:
                flights_list.append(response.json()['data'])
                print(f'Created flight {flight_index}/{total_flights}...')
                flight_index += 1
            else:
                print(response.json())
        flight_dict[airline['airline']['id']] = flights_list

    # Create tickets
    tickets_dict = {}
    ticket_index = 1
    total_tickets = tickets * total_flights
    for airline, flights in flight_dict.items():
        for flight in flights:
            tickets_dict[flight['id']] = {}
            tickets_list = []
            for index in range(tickets):
                customer = customers_list[randint(0, len(customers_list) - 1)]
                auth = HTTPBasicAuth(customer['user']['username'], customer['user']['password'])
                
                request_body = {
                    'flight_id': int(flight['id']),
                    'seat_count': randint(1,5) 
                }
                response = requests.post(BASE_URL + "tickets/", data=request_body, auth=auth)
                if response.status_code == 201:
                    tickets_list.append(response.json()['data'])
                    print(f'Created ticket {ticket_index}/{total_tickets}...')
                    ticket_index += 1
                else:
                    print(response.json())
                    
            tickets_dict[flight['id']] = tickets_list
                    
    output_dict = {
        'admins': admins_list,
        'airlines': airlines_list,
        'customers': customers_list,
        'flights': flight_dict,
        'tickets': tickets_dict
    }
    
    with open(OUTPUT_FILE, "w") as outfile:
        json.dump(output_dict, outfile, indent=4)
        
if __name__ == "__main__":
    generate_data()