from unittest import TestCase
from unittest.mock import MagicMock, patch

from FlightsApi.repository.repository_utils import Paginate

from datetime import datetime, timedelta

from FlightsApi.facades.facades import AdministratorFacade, AirlineFacade, CustomerFacade, AnonymousFacade, FacadeBase # Imports to test
from FlightsApi.facades.facades import R, RepoErrors, is_customer, is_airline, is_admin, DBTables # Imports for mocking etc.

class TestFacadeBase(TestCase):
    @patch('FlightsApi.facades.facades.R.get_all')
    def test_get_all_flights(self, mock_repo):
        with self.subTest('Success'):
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_all_flights(limit=1, page=1)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {'page': 1, 'limit': 1}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_all_flights()
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])
    
    
    @patch('FlightsApi.facades.facades.R.get_by_id')
    def test_get_flight_by_id(self, mock_repo):
        with self.subTest('Success'):
            mock_repo.return_value = {'success': True}
            result = FacadeBase.get_flight_by_id(1)
            mock_repo.assert_called_with(DBTables.FLIGHT, 1)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': {'success': True}}
            )
        
        with self.subTest('Not found failure'):
            mock_repo.return_value = {}
            result = FacadeBase.get_flight_by_id(1)
            self.assertEqual(result[0], 404)
            self.assertIn('not found', result[1]['error'])
        
        with self.subTest('Out of bounds failure'):
            mock_repo.side_effect = RepoErrors.OutOfBoundsException()
            result = FacadeBase.get_flight_by_id(1)
            self.assertEqual(result[0], 400)
            self.assertIn('larger than 0', result[1]['error'])
        
        with self.subTest('Unexpected failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_flight_by_id(1)
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])
    
    
    @patch('FlightsApi.facades.facades.Paginate')
    @patch('FlightsApi.facades.facades.R.get_flights_by_parameters')
    def test_get_flights_by_parameters(self, mock_repo, mock_paginate):
        with self.subTest('Success'):
            pagination = Paginate(1, 2)
            mock_paginate.return_value = pagination
            
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_flights_by_parameters(origin_country_id=1, destination_country_id=2, date=3, limit=4, page=5)
            
            mock_repo.assert_called_with(1,2,3,pagination)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {'page': 2, 'limit': 1}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_flights_by_parameters()
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])
    
    
    @patch('FlightsApi.facades.facades.R.get_by_id')
    def test_get_airline_by_id(self, mock_repo):
        with self.subTest('Success'):
            mock_repo.return_value = {'success': True}
            result = FacadeBase.get_airline_by_id(1)
            mock_repo.assert_called_with(DBTables.AIRLINECOMPANY ,1)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': {'success': True}}
            )
        
        with self.subTest('Not found failure'):
            mock_repo.return_value = {}
            result = FacadeBase.get_airline_by_id(1)
            self.assertEqual(result[0], 404)
            self.assertIn('not found', result[1]['error'])
        
        with self.subTest('Out of bounds failure'):
            mock_repo.side_effect = RepoErrors.OutOfBoundsException()
            result = FacadeBase.get_airline_by_id(1)
            self.assertEqual(result[0], 400)
            self.assertIn('larger than 0', result[1]['error'])
        
        with self.subTest('Unexpected failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_airline_by_id(1)
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])
    
    @patch('FlightsApi.facades.facades.Paginate')
    @patch('FlightsApi.facades.facades.R.get_airlines_by_name')
    def test_get_airlines_by_name(self, mock_repo, mock_pagination):
        with self.subTest('Success'):
            pagination = Paginate(1, 2)
            mock_pagination.return_value = pagination
            
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_airlines_by_name('abcd', limit=1, page=2)
            
            mock_pagination.assert_called_with(1, 2)
            mock_repo.assert_called_with('abcd', pagination, False)
            
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {'page': 2, 'limit': 1}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_airlines_by_name('abcd')
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])

    @patch('FlightsApi.facades.facades.Paginate')
    @patch('FlightsApi.facades.facades.R.get_all')
    def test_get_all_countries(self, mock_repo, mock_paginate):
        with self.subTest('Success'):
            pagination = Paginate(1, 2)
            mock_paginate.return_value = pagination
            
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_all_countries(limit=1, page=1)
            mock_paginate.assert_called_with(per_page=1, page_number=1)
            mock_repo.assert_called_with(DBTables.COUNTRY, pagination)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {'page': 2, 'limit': 1}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_all_countries()
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])
    
    @patch('FlightsApi.facades.facades.R.get_by_id')
    def test_get_country_by_id(self, mock_repo):
        with self.subTest('Success'):
            mock_repo.return_value = {'success': True}
            result = FacadeBase.get_country_by_id(1)
            mock_repo.assert_called_with(DBTables.COUNTRY ,1)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': {'success': True}}
            )
        
        with self.subTest('Not found failure'):
            mock_repo.return_value = {}
            result = FacadeBase.get_country_by_id(1)
            self.assertEqual(result[0], 404)
            self.assertIn('not found', result[1]['error'])
        
        with self.subTest('Out of bounds failure'):
            mock_repo.side_effect = RepoErrors.OutOfBoundsException()
            result = FacadeBase.get_country_by_id(1)
            self.assertEqual(result[0], 400)
            self.assertIn('larger than 0', result[1]['error'])
        
        with self.subTest('Unexpected failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_country_by_id(1)
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])


class TestAdminFacade(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with patch('FlightsApi.facades.facades.R.get_or_create_group') as mock:
            mock.return_value = {'id': 1, 'name': 'admin'}
            cls.facade = AdministratorFacade({
                'id': 1,
                'username': 'testadmin',
                'email': 'test@admin.com',
                'admin': 1,
                'is_active': True,
                'groups': [1]
            })
        return super().setUpClass()
    
    @patch('FlightsApi.facades.facades.Paginate')
    @patch('FlightsApi.facades.facades.R.get_all')
    def test_get_all_customers(self, mock_repo, mock_paginate):
        with self.subTest('Success'): 
            pagination = Paginate(1, 2)
            mock_paginate.return_value = pagination
            
            mock_repo.return_value = [{'success': True}]
            result = self.facade.get_all_customers(limit=1, page=2)
            mock_paginate.assert_called_with(per_page=1, page_number=2)
            mock_repo.assert_called_with(DBTables.CUSTOMER, pagination)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {'page': 2, 'limit': 1}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = self.facade.get_all_customers()
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])


    @patch('FlightsApi.facades.facades.R')
    def test_add_airline_success(self, mock_repo):
        mock_repo.add.return_value = {'id': 1}, True
        mock_repo.assign_group_to_user.return_value = None
        mock_repo.instance_exists.side_effect = [True, True]
        result = self.facade.add_airline(
            username='username',
            password='password',
            email='email',
            name='name',
            country_id=1
        )
        # Assertions
        self.assertEqual(result, (201, {'data': {'airline': {'id': 1}, 'user': {'id': 1}}}))
        
    @patch('FlightsApi.facades.facades.R')
    def test_add_airline_repo_errors(self, mock_repo):
        # Mocks
        def reset_mocks():
            # Set mocks back to success values.
            mock_repo.reset_mock(return_value=True)
        
            mock_repo.add.side_effect = None
            mock_repo.add.return_value = ({'id': 1}, True)
            
            mock_repo.instance_exists.side_effect = [True, True]
            
            mock_repo.assign_group_to_user.side_effect = None
            mock_repo.assign_group_to_user.return_value = None

        # User creation
        with self.subTest('Validation error'):
            reset_mocks()
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception'):
            reset_mocks()
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('User not created'):
            reset_mocks()
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 400) 
            self.assertIn('SomeError', result[1]['error'])
            
        # Adding user to group
        with self.subTest('User already in a group'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 409) 
            self.assertIn('already in a group', result[1]['error'])
        
        with self.subTest('Unexpected exception from assign_group_to_user'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Country verification
        with self.subTest('Country does not exist'):
            reset_mocks()
            mock_repo.instance_exists.side_effect = [False, True]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 400) 
            self.assertIn('does not exist', result[1]['error'])
            
        # Airline creation
        with self.subTest('Validation error on airline creation'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 400)
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Airline result verification
        with self.subTest('Airline creation failure'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ({'fieldError': 1}, False)]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result[0], 400) 
            self.assertIn('fieldError', result[1]['error'])
    

    @patch('FlightsApi.facades.facades.R')
    def test_add_customer_success(self, mock_repo):
        mock_repo.add.return_value = {'id': 1}, True
        mock_repo.assign_group_to_user.return_value = None
        result = self.facade.add_customer(
            username='username',
            password='password',
            email='email',
            first_name='first_name',
            last_name='last_name',
            address='address',
            phone_number='phonenumber'
        )
        # Assertions
        self.assertEqual(result, (201, {'data': {'customer': {'id': 1}, 'user': {'id': 1}}}))
        
    @patch('FlightsApi.facades.facades.R')
    def test_add_customer_repo_errors(self, mock_repo):
        # Mocks
        def reset_mocks():
            # Set mocks back to success values.
            mock_repo.add.reset_mock(return_value=True, side_effect=True)
            mock_repo.add.return_value = ({'id': 1}, True)
            
            mock_repo.assign_group_to_user.reset_mock(return_value=True, side_effect=True)
            mock_repo.assign_group_to_user.return_value = None
            
            mock_repo.instance_exists.reset_mock(return_value=True, side_effect=True)
            mock_repo.instance_exists.side_effect = [True, True]

        # User creation
        with self.subTest('User creation validation error'):
            reset_mocks()
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception at user creation'):
            reset_mocks()
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('User creation failure'):
            reset_mocks()
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, { 'error': {'SomeError': ['error']} }))
            
        # Adding user to group
        with self.subTest('User not found in assign_group_to_user'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = RepoErrors.EntityNotFoundException()
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('User already in a group'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException()
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 409) 
            self.assertIn('already in a group', result[1]['error'])
        
        with self.subTest('Unexpected exception'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Customer creation
        with self.subTest('Validation exception on customer creation'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception on customer creation'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Customer result verification
        with self.subTest('Customer creation failure'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ({'fieldError': 1}, False)]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 400) 
            self.assertIn('fieldError', result[1]['error'])
    

    @patch('FlightsApi.facades.facades.R')
    def test_add_administrator_success(self, mock_repo):
        mock_repo.add.return_value = {'id': 1}, True
        mock_repo.assign_group_to_user.return_value = None
        result = self.facade.add_administrator(
            username='username',
            password='password',
            email='email',
            first_name='first_name',
            last_name='last_name'
        )
        # Assertions
        self.assertEqual(result, (201, {'data': {'admin': {'id': 1}, 'user': {'id': 1}}}))
        
    @patch('FlightsApi.facades.facades.R')
    def test_add_administrator_repo_errors(self, mock_repo):
        # Mocks
        def reset_mocks():
            # Set mocks back to success values.
            mock_repo.add.reset_mock(return_value=True, side_effect=True)
            mock_repo.add.return_value = ({'id': 1}, True)
            
            mock_repo.assign_group_to_user.reset_mock(return_value=True, side_effect=True)
            mock_repo.assign_group_to_user.return_value = None
            
            mock_repo.instance_exists.reset_mock(return_value=True, side_effect=True)
            mock_repo.instance_exists.side_effect = [True, True]

        # User creation
        with self.subTest('User creation validation error'):
            reset_mocks()
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('User creation unexpected exception'):
            reset_mocks()
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('User not created'):
            reset_mocks()
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 400) 
            self.assertIn('SomeError', result[1]['error'])
            
        with self.subTest('User already in a group'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 409) 
            self.assertIn('already in a group', result[1]['error'])
        
        with self.subTest('Unexpected exception in assign_group_to_user'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Admin creation
        with self.subTest('Validation error on admin creation'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception on admin creation'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Admin result verification
        with self.subTest('Admin not created'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ({'fieldError': 1}, False)]
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result[0], 400) 
            self.assertIn('fieldError', result[1]['error'])

    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_airline_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
        mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        result = self.facade.deactivate_airline(1)
        self.assertEqual(result, (204, None))
    
    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_airline_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        with self.subTest('Airline id out of bounds'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result[0], 400) 
            self.assertIn('larger than 0', result[1]['error'])
            
        with self.subTest('Airline not found'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {}
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not found', result[1]['error'])
            
        with self.subTest('User not found on update'):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])
            
        with self.subTest('unexpected exception on update'):
            reset_mocks()
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('user not updated'):
            reset_mocks()
            mock_repo.update.return_value = {'is_active': True}, False
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            

    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_customer_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
        mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        result = self.facade.deactivate_customer(1)
        self.assertEqual(result, (204, None))
    
    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_customer_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        with self.subTest('Customer id out of bounds'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result[0], 400) 
            self.assertIn('larger than 0', result[1]['error'])
            
        with self.subTest('Unexpected exception at get_by_id'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = Exception('Some error')
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Customer not found'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {}
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not found', result[1]['error'])
            
        with self.subTest('User fetch error at user update'):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])
            
        with self.subTest('Unexpected exception at user update'):
            reset_mocks()
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Update failed'):
            reset_mocks()
            mock_repo.update.return_value = {'is_active': True}, False
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])

    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_administrator_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
        mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        result = self.facade.deactivate_administrator(1)
        self.assertEqual(result, (204, None))
    
    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_administrator_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        with self.subTest('Admin id out of bounds'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result[0], 400) 
            self.assertIn('larger than 0', result[1]['error'])
        
        with self.subTest('Unexpected exception on get_by_id'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = Exception('Some error')
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Admin not found'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {}
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not found', result[1]['error'])
            
        with self.subTest('Fetch error at update'):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])
            
        with self.subTest('Unexpected exception at update'):
            reset_mocks()
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Update failed'):
            reset_mocks()
            mock_repo.update.return_value = {'is_active': True}, False
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])



class TestAirlineFacade(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with patch('FlightsApi.facades.facades.R.get_or_create_group') as mock:
            mock.return_value = {'id': 1, 'name': 'airline'}
            cls.facade = AirlineFacade({
                'id': 1,
                'username': 'testairline',
                'email': 'test@airline.com',
                'airline': 1,
                'is_active': True,
                'groups': [1]
            })
        return super().setUpClass()
    
    @patch('FlightsApi.facades.facades.R')
    def test_get_my_flights(self, mock_repo):
        with self.subTest('Success'):
            mock_repo.get_flights_by_airline_id.return_value = [{'success': True}]
            result = self.facade.get_my_flights(limit=1, page=1)
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {'page': 1, 'limit': 1}}
            )
        
        with self.subTest('Failure'):
            mock_repo.get_flights_by_airline_id.side_effect = Exception("Example failure")
            result = self.facade.get_my_flights()
            self.assertEqual(result[0], 500)
            self.assertIn('unexpected error', result[1]['error'])
    
    @patch('FlightsApi.facades.facades.R')
    def test_update_airline_success(self, mock_repo):
        # Mocking
        mock_repo.update.return_value = ({'Success': True}, True)
        # Function call
        result = self.facade.update_airline(name='name', country_id=1)
        # Assertions
        self.assertEqual(result, (200, {'data': {'Success': True}}))
        mock_repo.update.assert_called_with(DBTables.AIRLINECOMPANY, 1, name='name', country_id=1)
        
    
    @patch('FlightsApi.facades.facades.R')
    def test_update_airline_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.reset_mock()
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = ({'Success': True}, True)
        
        with self.subTest('Airline not found'):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError()
            result = self.facade.update_airline(name='name', country_id=1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])
            
        with self.subTest('Validation errors'):
            reset_mocks()
            mock_repo.update.side_effect = ValueError('Some error')
            result = self.facade.update_airline(name='name', country_id=1)
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception'):
            reset_mocks()
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.update_airline(name='name', country_id=1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_flight_success(self, mock_repo):
        # Mocking
        mock_repo.add.return_value = {'success': True}, True

        time1 = datetime.now()
        time2 = time1 + timedelta(days=1)
        
        # Function call
        result = self.facade.add_flight(1, 1, time1, time2, 1)
                
        # Assertions
        self.assertEqual(
            result,
            (201, {'data': {'success': True}})
        )
        mock_repo.add.assert_called_with(
            DBTables.FLIGHT,
            airline=1,
            origin_country=1,
            destination_country=1,
            departure_datetime=time1,
            arrival_datetime=time2,
            total_seats=1
        )
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_flight_errors(self, mock_repo):
        time1 = datetime.now()
        time2 = time1 + timedelta(days=1)
        
        def reset_mocks():
            mock_repo.reset_mock()
            
            mock_repo.add.reset_mock(return_value=True, side_effect=True)
            mock_repo.add.return_value = ({'Success': True}, True)
        
        with self.subTest('Validation errors'):
            reset_mocks()
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_flight(1, 1, time1, time2, 1)
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
    
        with self.subTest('Unexpected exception'):
            reset_mocks()
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_flight(1, 1, time1, time2, 1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Failed addition'):
            reset_mocks()
            mock_repo.add.return_value = ({'fieldError': False}, False)
            result = self.facade.add_flight(1, 1, time1, time2, 1)
            self.assertEqual(result[0], 400) 
            self.assertIn('fieldError', result[1]['error'])
            
            
    @patch('FlightsApi.facades.facades.R')
    def test_update_flight_success(self, mock_repo):
        # Mocking
        mock_repo.get_by_id.return_value = {'airline': 1}
        mock_repo.update.return_value = {'success': True}, True
        
        # Function call
        result = self.facade.update_flight(1, total_seats=1)
                
        # Assertions
        self.assertEqual(
            result,
            (200, {'data': {'success': True}})
        )
        mock_repo.get_by_id.assert_called_with(DBTables.FLIGHT, 1)
        mock_repo.update.assert_called_with(DBTables.FLIGHT, id=1, total_seats=1)
    
    @patch('FlightsApi.facades.facades.R')
    def test_update_flight_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.reset_mock()
            
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'airline': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'success': True}, True

        with self.subTest('ID out of bounds'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 400) 
            self.assertIn('larger than 0', result[1]['error'])

        with self.subTest('Unexpected exception at get_by_id'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = Exception('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Flight not found'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {}
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not found', result[1]['error'])

        with self.subTest('Flight owned by different airline'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {'airline': 2}
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 403) 
            self.assertIn('do not own', result[1]['error'])

        with self.subTest("Repo can't find flight"):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])

        with self.subTest('Validation error with updated fields'):
            reset_mocks()
            mock_repo.update.side_effect = ValueError('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])

        with self.subTest('Unexpected error'):
            reset_mocks()
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
    
        with self.subTest('Update failure'):
            reset_mocks()
            mock_repo.update.return_value = (['Some error'], False)
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(result[0], 400) 
            self.assertIn('Some error', result[1]['error'])
    
    @patch('FlightsApi.facades.facades.R')
    def test_cancel_flight_success(self, mock_repo):
        # Mock setup
        mock_repo.get_by_id.return_value = {'airline': 1}
        mock_repo.update.return_value = ({'is_canceled': True}, True)
        # Function call
        result = self.facade.cancel_flight(1)
        # Assertions
        self.assertEqual(result[0], 204) 
        mock_repo.get_by_id.assert_called_with(DBTables.FLIGHT, 1)
        mock_repo.update.assert_called_with(DBTables.FLIGHT, id=1, is_canceled=True)
    
    @patch('FlightsApi.facades.facades.R')
    def test_cancel_flight_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.reset_mock()
            
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'airline': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = ({'is_canceled': True}, True)
            
        with self.subTest('Flight ID out of bounds'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException("Some error")
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 400) 
            self.assertIn('larger than 0', result[1]['error'])
        
        with self.subTest('Get flight - unexpected exception'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = Exception('Some error')
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Flight not found'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {}
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not found', result[1]['error'])
            
        with self.subTest('Flight owned by other airline'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {'airline': 2}
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 403) 
            self.assertIn('do not own', result[1]['error'])
    
        with self.subTest('Flight not found in repo.update()'):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])
            
        with self.subTest('Validation error on some updated field'):
            reset_mocks()
            mock_repo.update.side_effect = TypeError('Some error')
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception on update'):
            reset_mocks()
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Failed update'):
            reset_mocks()
            mock_repo.update.return_value = ({'is_canceled': False}, False)
            result = self.facade.cancel_flight(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
    

class TestCustomerFacade(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with patch('FlightsApi.facades.facades.R.get_or_create_group') as mock:
            mock.return_value = {'id': 1, 'name': 'customer'}
            cls.facade = CustomerFacade({
                'id': 1,
                'username': 'testcustomer',
                'email': 'test@customer.com',
                'customer': 1,
                'is_active': True,
                'groups': [1]
            })
        return super().setUpClass()
    
    @patch('FlightsApi.facades.facades.R')
    def test_update_customer_success(self, mock_repo):
        # Mock
        mock_repo.update.return_value = {'success': True}, True
        # Call function
        result = self.facade.update_customer(first_name='first_name')
        # Assertions
        self.assertEqual(result, (200, {'data': {'success': True}}))
        mock_repo.update.assert_called_with(DBTables.CUSTOMER, 1, first_name='first_name')
    
    @patch('FlightsApi.facades.facades.R')
    def test_update_customer_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.reset_mock()
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'success': True}, True
            
        with self.subTest('Customer not found'):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])
            
        with self.subTest('Validation error'):
            reset_mocks()
            mock_repo.update.side_effect = TypeError('Some error')
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception'):
            reset_mocks()
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Failed update'):
            reset_mocks()
            mock_repo.update.return_value = {'success': False}, False
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result[0], 400) 
            self.assertIn('success', result[1]['error'])
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_ticket_success(self, mock_repo):
        mock_repo.is_flight_bookable.return_value = True, ''
        mock_repo.add.return_value = {'success': True}, True
        
        result = self.facade.add_ticket(1, 2)
        
        self.assertEqual(result, (201, {'data': {'success': True}}))
        mock_repo.is_flight_bookable.assert_called_with(1, 2)
        mock_repo.add.assert_called_with(DBTables.TICKET, flight=1, customer=1, seat_count=2)
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_ticket_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.reset_mock()
            
            mock_repo.is_flight_bookable.reset_mock(return_value=True, side_effect=True)
            mock_repo.is_flight_bookable.return_value = True, ''
            
            mock_repo.add.reset_mock(return_value=True, side_effect=True)
            mock_repo.add.return_value = {'success': True}, True
    
        with self.subTest('Flight not bookable'):
            reset_mocks()
            mock_repo.is_flight_bookable.return_value = False, 'some reason'
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result[0], 409) 
            self.assertIn('some reason', result[1]['error'])
    
        with self.subTest('Value error'):
            reset_mocks()
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
    
        with self.subTest('Unexpected Exception'):
            reset_mocks()
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
    
        with self.subTest('Failed addition'):
            reset_mocks()
            mock_repo.add.return_value = {'success': False}, False
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result, (400, {'error': {'success': False}}))
    
    @patch('FlightsApi.facades.facades.R')
    def test_cancel_ticket_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'customer': 1}
        mock_repo.update.return_value = {'is_canceled': True}, True
        
        result = self.facade.cancel_ticket(1)
        
        self.assertEqual(result, (200, {'data': {'is_canceled': True}}))
        mock_repo.get_by_id.assert_called_with(DBTables.TICKET, 1)
        mock_repo.update.assert_called_with(DBTables.TICKET, id=1, is_canceled=True)
    
    @patch('FlightsApi.facades.facades.R')
    def test_cancel_ticket_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.reset_mock()
            
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'customer': 1}
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'is_canceled': True}, True
            
        with self.subTest('ID out of bounds'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException('Some error')
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result[0], 400) 
            self.assertIn('larger than 0', result[1]['error'])
            
        with self.subTest('Unexpected error in get_by_id'):
            reset_mocks()
            mock_repo.get_by_id.side_effect = Exception('Some error')
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('Ticket not found'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {}
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not found', result[1]['error'])
            
        with self.subTest('Ticket not owned by user'):
            reset_mocks()
            mock_repo.get_by_id.return_value = {'customer': 2}
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result[0], 403) 
            self.assertIn('do not own', result[1]['error'])
            
        with self.subTest('Ticket not found in update'):
            reset_mocks()
            mock_repo.update.side_effect = RepoErrors.FetchError()
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result[0], 404) 
            self.assertIn('not fetch', result[1]['error'])
            
        with self.subTest('Value error in update'):
            reset_mocks()
            mock_repo.update.side_effect = ValueError('Some error')
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest("Ticket wasn't updated"):
            reset_mocks()
            mock_repo.update.return_value = {'is_canceled': False}, False
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
    

class TestAnonymousFacade(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facade = AnonymousFacade()
        return super().setUpClass()
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_customer_success(self, mock_repo):
        mock_repo.add.return_value = {'id': 1}, True
        mock_repo.assign_group_to_user.return_value = None
        result = self.facade.add_customer(
            username='username',
            password='password',
            email='email',
            first_name='first_name',
            last_name='last_name',
            address='address',
            phone_number='phonenumber'
        )
        # Assertions
        self.assertEqual(result, (201, {'data': {'customer': {'id': 1}, 'user': {'id': 1}}}))
        
    @patch('FlightsApi.facades.facades.R')
    def test_add_customer_repo_errors(self, mock_repo):
        # Mocks
        def reset_mocks():
            mock_repo.reset_mock()
            # Set mocks back to success values.
            mock_repo.add.reset_mock(return_value=True, side_effect=True)
            mock_repo.add.return_value = ({'id': 1}, True)
            
            mock_repo.assign_group_to_user.reset_mock(return_value=True, side_effect=True)
            mock_repo.assign_group_to_user.return_value = None
            
            mock_repo.instance_exists.reset_mock(return_value=True, side_effect=True)
            mock_repo.instance_exists.side_effect = [True, True]

        # User creation
        with self.subTest('User creation validation error'):
            reset_mocks()
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 400) 
            self.assertIn('Some error', result[1]['error'])
            
        with self.subTest('Unexpected exception at user creation'):
            reset_mocks()
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        with self.subTest('User creation failure'):
            reset_mocks()
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 400) 
            self.assertIn('SomeError', result[1]['error'])
            
        # Adding user to group
        with self.subTest('User already in a group'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 409) 
            self.assertIn('already in a group', result[1]['error'])
        
        with self.subTest('Unexpected exception'):
            reset_mocks()
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Customer creation
        with self.subTest('Validation exception on customer creation'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 400) 
            self.assertIn('passed values', result[1]['error'])
            
        with self.subTest('Unexpected exception on customer creation'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 500) 
            self.assertIn('unexpected error', result[1]['error'])
            
        # Customer result verification
        with self.subTest('Customer creation failure'):
            reset_mocks()
            mock_repo.add.side_effect = [({'id': 1}, True), ({'fieldError': 1}, False)]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result[0], 400) 
            self.assertIn('fieldError', result[1]['error'])
    
    