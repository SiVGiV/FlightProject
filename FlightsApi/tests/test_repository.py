from django.test import TestCase

from ..repository.repository import Repository, DBTables
from ..repository.errors import *
from ..repository.repository_utils import Paginate

from ..utils.exceptions import IncorrectTypePassedToFunctionException
from ..models import User, Admin, AirlineCompany, Customer, Country, Flight, Ticket

from django.utils import timezone
from datetime import timedelta, date


class TestGetById(TestCase):
    def test_get_by_id_success(self):
        # Test a full success
        user = User.objects.create_user("testUser", "test@a.com")
        customer = Customer.objects.create(
            first_name="testy",
            last_name="testson",
            address="123 test st.",
            phone_number="+972 1231212",
            credit_card_number="1234 1234 1234 1234",
            user=user
        )
        
        with self.subTest("User by ID"):
            user_from_repo = Repository.get_by_id(DBTables.USER, user.id)
            self.assertEqual(user_from_repo['id'], user.id)
        with self.subTest("Customer by ID"):
            customer_from_repo = Repository.get_by_id(DBTables.CUSTOMER, customer.id)
            self.assertEqual(customer_from_repo['id'], customer.id)
        
    def test_get_by_id_with_non_existing_id(self):
        # Test non existing ID - Expects an empty dict
        self.assertDictEqual({}, Repository.get_by_id(DBTables.AIRLINECOMPANY, 1))
    
    def test_get_by_id_bad_id_type(self):
        # Test wrong type passed as ID - expects an error thrown by the '@accepts' decorator
        self.assertRaises(IncorrectTypePassedToFunctionException, lambda: Repository.get_by_id(DBTables.USER, "jeff"))
    
    def test_get_by_id_bad_model(self):
        # Test wrong type passed as dbtable - expects an error thrown by the '@accepts' decorator
        self.assertRaises(IncorrectTypePassedToFunctionException, lambda: Repository.get_by_id(User, 1))
    
    def test_get_by_id_bad_id_value(self):
        # Test ID outside of normal parameters (Negative or Zero) - expects an OutOfBoundsException error
        self.assertRaises(OutOfBoundsException, lambda: Repository.get_by_id(DBTables.USER, -1))
        

class TestGetAll(TestCase):
    def test_get_all_success(self):
        # Test success
        users = []
        with self.subTest("Empty database"):
            # Checks that the result is empty when the database is.
            self.assertEqual(len(users), len(Repository.get_all(DBTables.USER)))
            
        user1 = User.objects.create_user("testUser1", "test1@a.com", "test1234")
        users.append(user1)
        with self.subTest("Single entry"):
            repo_result = Repository.get_all(DBTables.USER)
            # Check that the amount of retrieved results is correct.
            self.assertEqual(len(users), len(repo_result))
            # Check one of the entries to see that it is returned properly.
            self.assertEqual(user1.pk, repo_result[0]['id'])
            
        user2 = User.objects.create_user("testUser2", "test2@a.com", "test2345")
        users.append(user2)
        with self.subTest("Multiple Entries"):
            # Check that the amount of retrieved results is correct.
            self.assertEqual(len(users), len(Repository.get_all(DBTables.USER)))
            
        user3 = User.objects.create_user("testUser3", "test3@a.com", "test3456")
        users.append(user3)
        with self.subTest("Paginated Entries"):
            # Check that the amount of paginated results is correct.
            page1 = Repository.get_all(DBTables.USER, Paginate(2,1))
            self.assertEqual(2, len(page1))
            page2 = Repository.get_all(DBTables.USER, Paginate(2,2))
            self.assertEqual(1, len(page2))
    

class TestAdd(TestCase):
    def test_add_success(self):
        user = Repository.add( 
                DBTables.USER,
                username="testUser",
                email="test@a.com",
                password="test1234"
            )[0]
        customer = Repository.add(
                DBTables.CUSTOMER,
                first_name="testy",
                last_name="testson",
                address="123 test st.",
                phone_number="+972 1231212",
                credit_card_number="1234 1234 1234 1234",
                user=user['id']
            )[0]
        with self.subTest("User creation"):
            user_from_db = User.objects.filter(id=user["id"]).first()
            self.assertEqual(user['username'], user_from_db.username)
        with self.subTest("Customer creation"):
            customer_from_db = Customer.objects.filter(id=customer["id"]).first()
            self.assertEqual(customer['first_name'], customer_from_db.first_name)
            
    def test_bad_data(self):
        with self.subTest("Missing Fields"):
            self.assertEqual(False, Repository.add(DBTables.USER, email="a@a.com", password="test123")[1])
        with self.subTest("Wrong field type"):
            self.assertEqual(False, Repository.add(DBTables.ADMIN, first_name="admin", last_name="admin", user="bad field")[1])


class TestUpdate(TestCase):
    def test_update_success(self):
        user = User.objects.create_user("test", "a@a.com", "1234")
        repo_result = Repository.update(DBTables.USER, user.id, email="b@b.com")
        updated_user = User.objects.get(id=user.id)
        self.assertEqual(updated_user.email, "b@b.com")
        self.assertEqual(repo_result[0]['email'], "b@b.com")

    def test_update_non_existing_id(self):
        self.assertRaises(FetchError, lambda: Repository.update(DBTables.USER, 1, email="b@b.com"))
        
    def test_update_no_fields(self):
        user = User.objects.create_user("test", "a@a.com", "1234")
        self.assertEqual(user.username, Repository.update(DBTables.USER, user.id)[0]['username'])
        
    def test_update_attribute_errors(self):
        user = User.objects.create_user("test", "a@a.com", "1234")
        with self.subTest("Non existing attribute"):
            repo_result = Repository.update(DBTables.USER, user.id, fakefield="fakevalue")
            self.assertEqual(True, repo_result[1])
        with self.subTest("Bad type"):
            repo_result = Repository.update(DBTables.USER, user.id, is_active="not bool")
            self.assertEqual(False, repo_result[1])


class TestAddAll(TestCase):
    def test_add_all_success(self):
        new_rows = [
            {'username': "test1", 'email': "a@a.com", 'password': "test1"},
            {'username': "test2", 'email': "b@b.com", 'password': "test2"}
        ]
        repo_result = Repository.add_all(DBTables.USER, new_rows)
        with self.subTest("Successfully added"):
            self.assertEqual(2, len(repo_result[0]))
        with self.subTest("Failed addition"):
            self.assertEqual(0, len(repo_result[1]))
    
    def test_add_some_successful(self):
        new_rows = [
            {'username': "test1", 'email': "a@a.com", 'password': "test1"},
            {'email': "b@b.com", 'password': "test2"},
        ]
        repo_result = Repository.add_all(DBTables.USER, new_rows)
        with self.subTest("Successfully added"):
            self.assertEqual(1, len(repo_result[0]))
        with self.subTest("Failed addition"): 
            self.assertEqual(1, len(repo_result[1]))
        
    
    def test_add_all_empty(self):
        repo_result = Repository.add_all(DBTables.USER, [{},{}])
        with self.subTest("Successfully added"):
            self.assertEqual(0, len(repo_result[0]))
        with self.subTest("Failed addition"):
            self.assertEqual(2, len(repo_result[1]))


class TestRemove(TestCase):
    def test_remove_success(self):
        user = User.objects.create_user("test1", "a@a.com", "1234")
        id = user.id
        Repository.remove(DBTables.USER, id)
        self.assertEqual(0, len(User.objects.filter(pk=id)))
        
    def test_remove_non_existing(self):
        try:
            Repository.remove(DBTables.USER, 1)
        except Exception as e:
            self.fail("Repository.remove() did not complete!")


class TestQueries(TestCase):
    def setUp(self) -> None:
        return_value = super().setUp() or None
        self.testing_data = {
            'users': [],
            'customers': [],
            'countries': [],
            'airlines': [],
            'flights': [],
            'tickets': []
        }
        
        # Create customers
        user1 = User.objects.create_user(username="customer1", email="user1@customer.com")
        user2 = User.objects.create_user(username="customer2", email="user2@customer.com")
        customer1 = Customer.objects.create(
            first_name="some",
            last_name="testing",
            address="123 test ave.",
            phone_number="+123 1234 1234",
            credit_card_number="4580 1234 5678 1111",
            user=user1
        )
        customer2 = Customer.objects.create(
            first_name="more",
            last_name="testing",
            address="123 test ave.",
            phone_number="+123 5678 5678",
            credit_card_number="4580 1234 5678 2222",
            user=user2
        )
        self.testing_data['users'].extend((user1, user2,))
        self.testing_data['customers'].extend((customer1, customer2,))
        
        # Create countries
        country1 = Country.objects.create(name="Israel", symbol="IL", flag="some/slug.jpg")
        country2 = Country.objects.create(name="Kazakhstan", symbol="KZ", flag="other/slug.jpg")
        self.testing_data['countries'].extend((country1, country2,))
        
        # Create airlines
        user3 = User.objects.create_user(username="airline1", email="user3@airline.com")
        user4 = User.objects.create_user(username="airline2", email="user4@airline.com")
        airline1 = AirlineCompany.objects.create(name="Django Airlines", country=country1, user=user3)
        airline2 = AirlineCompany.objects.create(name="React Airlines", country=country2, user=user4)
        self.testing_data['users'].extend((user3, user4,))
        self.testing_data['airlines'].extend((airline1, airline2,))

        # Create flights
        flight1 = Flight.objects.create(
            airline=airline1,
            origin_country=country1,
            destination_country=country2,
            departure_datetime=timezone.now() + timedelta(hours=1),
            arrival_datetime=timezone.now() + timedelta(hours=2),
            total_seats=1
        )
        flight2 = Flight.objects.create(
            airline=airline2,
            origin_country=country2,
            destination_country=country1,
            departure_datetime=timezone.now() + timedelta(weeks=1),
            arrival_datetime=timezone.now() + timedelta(weeks=1, days=1),
            total_seats=1
        )
        self.testing_data['flights'].extend((flight1, flight2,))
        
        # Create tickets
        ticket1 = Ticket.objects.create(flight=flight1, customer=customer1, seat_count=1)
        ticket2 = Ticket.objects.create(flight=flight1, customer=customer2, seat_count=1)
        ticket3 = Ticket.objects.create(flight=flight2, customer=customer1, seat_count=1)
        self.testing_data['tickets'].extend((ticket1, ticket2, ticket3,))
        
        return return_value
    
    def test_get_airline_by_username(self):
        with self.subTest("Success"):
            airline_id = self.testing_data['airlines'][0].id
            airline_username = self.testing_data['airlines'][0].user.username
            
            airline_from_repo = Repository.get_airline_by_username(airline_username)
            self.assertEqual(
                airline_id,
                airline_from_repo[0]['id']
            )
        
        with self.subTest("Empty result"):
            self.assertFalse(Repository.get_airline_by_username("NonExistent")[1])
            
        with self.subTest("Wrong type"):
            self.assertRaises(TypeError, lambda: Repository.get_airline_by_username(-1))
    
    def test_get_customer_by_username(self):
        with self.subTest("Success"):
            customer = self.testing_data['customers'][0]
            customer_id = customer.id
            customer_username = customer.user.username
            
            customer_from_repo = Repository.get_customer_by_username(customer_username)
            self.assertEqual(
                customer_id,
                customer_from_repo[0]['id']
            )
        
        with self.subTest("Empty result"):
            self.assertFalse(Repository.get_customer_by_username("NonExistent")[1])
            
        with self.subTest("Wrong Type"):
            self.assertRaises(TypeError, lambda: Repository.get_customer_by_username(-1))
    
    def test_get_user_by_username(self):
        with self.subTest("Success"):
            user_id = self.testing_data['users'][0].id
            user_username = self.testing_data['users'][0].username
            
            user_from_repo = Repository.get_user_by_username(user_username)
            self.assertEqual(
                user_id,
                user_from_repo[0]['id']
            )
        
        with self.subTest("Empty result"):
            self.assertFalse(Repository.get_user_by_username("NonExistent")[1])
            
        with self.subTest("Wrong type"):
            self.assertRaises(TypeError, lambda: Repository.get_user_by_username(-1))
    
    def test_get_flights_by_parameters(self):
        flight = self.testing_data['flights'][0]
        origin = flight.origin_country
        destination = flight.destination_country
        origin_datetime = flight.departure_datetime
        
        with self.subTest("Success"):
            result = Repository.get_flights_by_parameters(
                origin_country_id=origin.id,
                destination_country_id=destination.id,
                date=origin_datetime.date()
            )
            self.assertEqual(flight.id, result[0]['id'])
                
        with self.subTest("Empty result"):
            result = Repository.get_flights_by_parameters(
                origin_country_id=origin.id,
                destination_country_id=destination.id,
                date=(timezone.now() + timedelta(weeks=100)).date()
            )
            self.assertCountEqual([], result)
        
        with self.subTest("TypeError @ origin_country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_parameters("error", 1, date(2000, 1, 1)))
        
        with self.subTest("TypeError @ destination_country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_parameters(1, "error", date(2000, 1 ,1)))
        
        with self.subTest("TypeError @ date"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_parameters(1, 1, "error"))
    
    def test_get_flights_by_airline_id(self):
        airline = self.testing_data['airlines'][0]
        flight_list = [flight for flight in airline.flights.all()]
        flight_ids = [flight.id for flight in flight_list]
        
        with self.subTest("Success"):
            result = Repository.get_flights_by_airline_id(airline.id)
            result_ids = [flight['id'] for flight in result]
            self.assertListEqual(flight_ids, result_ids)
        
        with self.subTest("Empty result"):
            result = Repository.get_flights_by_airline_id(999)
            self.assertCountEqual([], result)
            
        with self.subTest("TypeError @ airline_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_airline_id("err"))
        
    def test_get_arrival_flights(self):
        soon_flight = self.testing_data['flights'][0] # This flight arrives in 2 hours
        soon_flight_id = self.testing_data['flights'][0].id
        soon_country_id = soon_flight.destination_country.id
        
        not_soon_flight = self.testing_data['flights'][1] # This flight arrives in a week
        not_soon_flight_id = self.testing_data['flights'][1].id
        not_soon_country_id = not_soon_flight.destination_country.id

        with self.subTest("Success"):
            results = Repository.get_arrival_flights(soon_country_id)
            self.assertIn(soon_flight_id, [flight['id'] for flight in results])
        
        with self.subTest("Empty result"):
            results = Repository.get_arrival_flights(soon_country_id)
            self.assertNotIn(
                not_soon_flight_id,
                Repository.get_arrival_flights(not_soon_country_id)    
            )
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_arrival_flights("err"))
    
    def test_get_departure_flights(self):
        soon_flight = self.testing_data['flights'][0] # This flight leaves in an hour
        soon_flight_id = soon_flight.id
        soon_country_id = soon_flight.origin_country.id
        
        not_soon_flight = self.testing_data['flights'][1] # This flight leaves in a week
        not_soon_flight_id = not_soon_flight.id
        not_soon_country_id = not_soon_flight.origin_country.id

        with self.subTest("Success"):
            results = Repository.get_departure_flights(soon_country_id)
            self.assertIn(soon_flight_id, [flight['id'] for flight in results])
        
        with self.subTest("Empty result"):
            results = Repository.get_departure_flights(not_soon_country_id)
            self.assertNotIn(
                not_soon_flight_id,
                [flight['id'] for flight in results]
            )
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_departure_flights("err"))
    
    def test_get_tickets_by_customer(self):
        customer = self.testing_data['customers'][0]
        customer_tickets = [ticket.id for ticket in customer.tickets.all()]
        
        with self.subTest("Success"):
            result = [ticket['id'] for ticket in Repository.get_tickets_by_customer(customer.id)]
            self.assertListEqual(customer_tickets, result)
        
        with self.subTest("Empty list"):
            result = Repository.get_tickets_by_customer(999)
            self.assertCountEqual([], result)
            
        with self.subTest("TypeError @ customer_id"):
            self.assertRaises(TypeError, lambda: Repository.get_tickets_by_customer("err"))
            
    def test_get_airlines_by_country(self):
        country = self.testing_data['countries'][0]
        airlines = [airline.id for airline in country.airlines.all()]
        
        with self.subTest("Success"):
            result = [airline['id'] for airline in Repository.get_airlines_by_country(country.id)]
            self.assertListEqual(airlines, result)
        
        with self.subTest("Empty list"):
            result = Repository.get_airlines_by_country(999)
            self.assertCountEqual([], result)
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_airlines_by_country("err"))
            
    def test_get_airlines_by_name(self):
        airlines = [self.testing_data['airlines'][0].id]
        
        with self.subTest("Full search"):
            result = [airline['id'] for airline in Repository.get_airlines_by_name("Django Airlines")]
            self.assertListEqual(airlines, result)
            
        with self.subTest("Partial search"):
            result = [airline['id'] for airline in Repository.get_airlines_by_name("django")]
            self.assertListEqual(airlines, result)
        
        with self.subTest("Empty list"):
            result = Repository.get_airlines_by_name("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            self.assertCountEqual([], result)
            
        with self.subTest("TypeError @ name"):
            self.assertRaises(TypeError, lambda: Repository.get_airlines_by_name(False))
            
            
    def test_get_flights_by_origin(self):
        country = self.testing_data['countries'][0]
        flights = [flight.id for flight in country.origin_flights.all()]
        
        with self.subTest("Success"):
            results = [flight['id'] for flight in Repository.get_flights_by_origin(country.id)]
            self.assertListEqual(flights, results)
        
        with self.subTest("Empty list"):
            results = Repository.get_flights_by_origin(999)
            self.assertCountEqual([], results)
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_origin("err"))
            
    def test_get_flights_by_destination(self):
        country = self.testing_data['countries'][0]
        flights = [flight.id for flight in country.destination_flights.all()]
        
        with self.subTest("Success"):
            results = [flight['id'] for flight in Repository.get_flights_by_destination(country.id)]
            self.assertListEqual(flights, results)
        
        with self.subTest("Empty list"):
            result = Repository.get_flights_by_destination(999)
            self.assertCountEqual([], result)
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_destination("err"))
    
    def test_get_flights_by_departure_date(self):
        flight = self.testing_data['flights'][0]
        flight_id = flight.id
        departure_date = flight.departure_datetime.date()
        
        with self.subTest("Success"):
            results = [flight['id'] for flight in Repository.get_flights_by_departure_date(departure_date)]
            self.assertIn(flight_id, results)
        
        with self.subTest("Empty list"):
            results = Repository.get_flights_by_departure_date(date(2000, 1, 1))
            self.assertCountEqual([], results)
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_departure_date("err"))  
    
    def test_get_flights_by_arrival_date(self):
        flight = self.testing_data['flights'][0]
        flight_id = flight.id 
        arrival_date = flight.arrival_datetime.date()
        
        with self.subTest("Success"):
            results = [flight['id'] for flight in Repository.get_flights_by_arrival_date(arrival_date)]
            self.assertIn(flight_id, results)
        
        with self.subTest("Empty list"):
            result = Repository.get_flights_by_arrival_date(date(2000, 1, 1))
            self.assertCountEqual([], result)
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_arrival_date("err"))  
    
    def test_get_flights_by_customer(self):
        ticket = self.testing_data['tickets'][0]
        customer_id = ticket.customer.id
        flight = ticket.flight
        flight_id = flight.id
        
        with self.subTest("Success"):
            result = [flight['id'] for flight in Repository.get_flights_by_customer(customer_id)]
            self.assertIn(flight_id, result)
        
        with self.subTest("Empty list"):
            result = Repository.get_flights_by_customer(999)
            self.assertCountEqual([], result)
            
        with self.subTest("TypeError @ country_id"):
            self.assertRaises(TypeError, lambda: Repository.get_flights_by_customer("err"))
    