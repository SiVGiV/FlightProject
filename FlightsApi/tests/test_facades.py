from unittest import TestCase
from unittest.mock import MagicMock, patch

from datetime import datetime, timedelta

from FlightsApi.facades.facades import AdministratorFacade, AirlineFacade, CustomerFacade, AnonymousFacade, FacadeBase # Imports to test
from FlightsApi.facades.facades import R, RepoErrors, is_customer, is_airline, is_admin, DBTables # Imports for mocking etc.

class TestFacadeBase(TestCase):    
    @patch.object(R, 'get_all')
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
            self.assertIn('Example failure', result[1]['errors'][1])
    
    
    @patch.object(R, 'get_by_id')
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
            self.assertIn('not found', result[1]['errors'][0])
        
        with self.subTest('Out of bounds failure'):
            mock_repo.side_effect = RepoErrors.OutOfBoundsException()
            result = FacadeBase.get_flight_by_id(1)
            self.assertEqual(result[0], 400)
            self.assertIn('must be larger than zero', result[1]['errors'][0])
        
        with self.subTest('Unexpected failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_flight_by_id(1)
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])
    
    
    @patch('FlightsApi.facades.facades.Paginate')
    @patch.object(R, 'get_flights_by_parameters')
    def test_get_flights_by_parameters(self, mock_repo, mock_paginate):
        with self.subTest('Success'):
            from FlightsApi.facades.facades import Paginate
            Paginate.return_value = {}
            
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_flights_by_parameters(origin_country_id=1, destination_country_id=2, date=3, limit=4, page=5)
            
            mock_repo.assert_called_with(1,2,3,{})
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_flights_by_parameters()
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])
    
    
    @patch('FlightsApi.facades.facades.Paginate')
    @patch.object(R, 'get_all')
    def test_get_all_airlines(self, mock_repo, mock_paginate):
        
        with self.subTest('Success'): 
            from FlightsApi.facades.facades import Paginate
            Paginate.return_value = {}
            Paginate.keys = MagicMock(return_value=())
            Paginate.__getitem__ = MagicMock(return_value=())
            
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_all_airlines(limit=1, page=1)
            mock_paginate.assert_called_with(1, 1)
            mock_repo.assert_called_with(DBTables.AIRLINECOMPANY, {})
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_all_airlines()
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])
    
    
    @patch.object(R, 'get_by_id')
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
            self.assertIn('not found', result[1]['errors'][0])
        
        with self.subTest('Out of bounds failure'):
            mock_repo.side_effect = RepoErrors.OutOfBoundsException()
            result = FacadeBase.get_airline_by_id(1)
            self.assertEqual(result[0], 400)
            self.assertIn('must be larger than zero', result[1]['errors'][0])
        
        with self.subTest('Unexpected failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_airline_by_id(1)
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])
    
    @patch('FlightsApi.facades.facades.Paginate')
    @patch('FlightsApi.facades.facades.R.get_airlines_by_name')
    def test_get_airlines_by_name(self, mock_repo, mock_pagination):
        with self.subTest('Success'):
            from FlightsApi.facades.facades import Paginate
            Paginate.return_value = {}
            Paginate.keys = MagicMock(return_value=())
            Paginate.__getitem__ = MagicMock(return_value=())
            
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_airlines_by_name('abcd', limit=1, page=1)
            
            mock_pagination.assert_called_with(1, 1)
            mock_repo.assert_called_with('abcd', {})
            
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_airlines_by_name('abcd')
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])

    @patch('FlightsApi.facades.facades.Paginate')
    @patch.object(R, 'get_all')
    def test_get_all_countries(self, mock_repo, mock_paginate):
        with self.subTest('Success'): 
            from FlightsApi.facades.facades import Paginate
            Paginate.return_value = {}
            Paginate.keys = MagicMock(return_value=())
            Paginate.__getitem__ = MagicMock(return_value=())
            
            mock_repo.return_value = [{'success': True}]
            result = FacadeBase.get_all_airlines(limit=1, page=1)
            mock_paginate.assert_called_with(1, 1)
            mock_repo.assert_called_with(DBTables.AIRLINECOMPANY, {})
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_all_airlines()
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])
    
    @patch.object(R, 'get_by_id')
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
            self.assertIn('not found', result[1]['errors'][0])
        
        with self.subTest('Out of bounds failure'):
            mock_repo.side_effect = RepoErrors.OutOfBoundsException()
            result = FacadeBase.get_country_by_id(1)
            self.assertEqual(result[0], 400)
            self.assertIn('must be larger than zero', result[1]['errors'][0])
        
        with self.subTest('Unexpected failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = FacadeBase.get_country_by_id(1)
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])


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
    @patch.object(R, 'get_all')
    def test_get_all_customers(self, mock_repo, mock_paginate):
        with self.subTest('Success'): 
            from FlightsApi.facades.facades import Paginate
            Paginate.return_value = {}
            Paginate.keys = MagicMock(return_value=())
            Paginate.__getitem__ = MagicMock(return_value=())
            
            mock_repo.return_value = [{'success': True}]
            result = self.facade.get_all_customers(limit=1, page=1)
            mock_paginate.assert_called_with(per_page=1, page_number=1)
            mock_repo.assert_called_with(DBTables.CUSTOMER, {})
            self.assertEqual(result[0], 200) # Check status code
            self.assertDictEqual( # Check response content
                result[1],
                {'data': [{'success': True}], 'pagination': {}}
            )
        
        with self.subTest('Failure'):
            mock_repo.side_effect = Exception("Example failure")
            result = self.facade.get_all_customers()
            self.assertEqual(result[0], 500)
            self.assertIn('Example failure', result[1]['errors'][1])


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
        self.assertEqual(result, (200, {'data': {'airline': {'id': 1}, 'user': {'id': 1}}}))
        
    @patch('FlightsApi.facades.facades.R')
    def test_add_airline_repo_errors(self, mock_repo):
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
        with self.subTest('first EXCEPT block'):
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('second EXCEPT block'):
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('first IF block'):
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (400, { 'errors': {'SomeError': ['error']} }))
            reset_mocks()
            
        # Adding user to group
        with self.subTest('third EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.EntityNotFoundException
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (400, {'errors': ['User ID 1 not found.']}))
            reset_mocks()
            
        with self.subTest('fourth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (409, {'errors': ['User ID 1 is already assigned to a role.']}))
            reset_mocks()
        
        with self.subTest('fifth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # User and country verification
        with self.subTest('second IF block'):
            mock_repo.instance_exists.side_effect = [False, True]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (400, {'errors': ['Country ID 1 not found.']}))
            reset_mocks()
            
        with self.subTest('third IF block'):
            mock_repo.instance_exists.side_effect = [True, False]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (400, {'errors': ['User ID 1 not found.']}))
            reset_mocks()
            
        # Airline creation
        with self.subTest('sixth except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some value error']}))
            reset_mocks()
            
        with self.subTest('seventh except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # Airline result verification
        with self.subTest('fourth IF block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ({'id': 1}, False)]
            result = self.facade.add_airline('username', 'password', 'email', 'name', 1)
            self.assertEqual(result, (400, {'errors': {'id': 1}}))
            reset_mocks()
    

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
        self.assertEqual(result, (200, {'data': {'customer': {'id': 1}, 'user': {'id': 1}}}))
        
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
        with self.subTest('first EXCEPT block'):
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('second EXCEPT block'):
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('first IF block'):
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, { 'errors': {'SomeError': ['error']} }))
            reset_mocks()
            
        # Adding user to group
        with self.subTest('third EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.EntityNotFoundException
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': ['User ID 1 not found.']}))
            reset_mocks()
            
        with self.subTest('fourth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (409, {'errors': ['User ID 1 is already assigned to a role.']}))
            reset_mocks()
        
        with self.subTest('fifth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # Airline creation
        with self.subTest('sixth except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some value error']}))
            reset_mocks()
            
        with self.subTest('seventh except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # Airline result verification
        with self.subTest('second IF block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ({'id': 1}, False)]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': {'id': 1}}))
            reset_mocks()
    

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
        self.assertEqual(result, (200, {'data': {'admin': {'id': 1}, 'user': {'id': 1}}}))
        
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
        with self.subTest('first EXCEPT block'):
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('second EXCEPT block'):
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('first IF block'):
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (400, { 'errors': {'SomeError': ['error']} }))
            reset_mocks()
            
        # Adding user to group
        with self.subTest('third EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.EntityNotFoundException
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (400, {'errors': ['User ID 1 not found.']}))
            reset_mocks()
            
        with self.subTest('fourth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (409, {'errors': ['User ID 1 is already assigned to a role.']}))
            reset_mocks()
        
        with self.subTest('fifth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # Airline creation
        with self.subTest('sixth except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some value error']}))
            reset_mocks()
            
        with self.subTest('seventh except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # Airline result verification
        with self.subTest('second IF block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ({'id': 1}, False)]
            result = self.facade.add_administrator('username', 'password', 'email', 'first_name', 'last_name')
            self.assertEqual(result, (400, {'errors': {'id': 1}}))
            reset_mocks()

    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_airline_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
        mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        result = self.facade.deactivate_airline(1)
        self.assertEqual(result, (200, {'data': {'success': True}}))
    
    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_airline_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        with self.subTest('first EXCEPT block'):
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result, (400, {'errors': ['Airline ID must be greater than 0.']}))
            reset_mocks()
            
        with self.subTest('first IF block'):
            mock_repo.get_by_id.return_value = {}
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result, (404, {'errors': [f'Could not find an airline with the ID 1']}))
            reset_mocks()
            
        with self.subTest('second EXCEPT block'):
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result, (404, {'errors': [f'Could not find a user matching an airline with the ID 1']}))
            reset_mocks()
            
        with self.subTest('third EXCEPT block'):
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('second IF block'):
            mock_repo.update.return_value = {'is_active': True}, False
            result = self.facade.deactivate_airline(1)
            self.assertEqual(result, (500, {'errors': ['Unexpected failure occured.']}))
            reset_mocks()
            

    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_customer_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
        mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        result = self.facade.deactivate_customer(1)
        self.assertEqual(result, (200, {'data': {'success': True}}))
    
    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_customer_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        with self.subTest('first EXCEPT block'):
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result, (400, {'errors': ['Customer ID must be greater than 0.']}))
            reset_mocks()
            
        with self.subTest('first IF block'):
            mock_repo.get_by_id.return_value = {}
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result, (404, {'errors': [f'Could not find a customer with the ID 1']}))
            reset_mocks()
            
        with self.subTest('second EXCEPT block'):
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result, (404, {'errors': [f'Could not find a user matching a customer with the ID 1']}))
            reset_mocks()
            
        with self.subTest('third EXCEPT block'):
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('second IF block'):
            mock_repo.update.return_value = {'is_active': True}, False
            result = self.facade.deactivate_customer(1)
            self.assertEqual(result, (500, {'errors': ['Unexpected failure occured.']}))
            reset_mocks()

    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_administrator_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
        mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        result = self.facade.deactivate_administrator(1)
        self.assertEqual(result, (200, {'data': {'success': True}}))
    
    @patch('FlightsApi.facades.facades.R')
    def test_deactivate_administrator_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'id': 1, 'user': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'id': 1, 'is_active': False}, True
        
        with self.subTest('first EXCEPT block'):
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result, (400, {'errors': ['Admin ID must be greater than 0.']}))
            reset_mocks()
            
        with self.subTest('first IF block'):
            mock_repo.get_by_id.return_value = {}
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result, (404, {'errors': [f'Could not find an admin with the ID 1']}))
            reset_mocks()
            
        with self.subTest('second EXCEPT block'):
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result, (404, {'errors': [f'Could not find a user matching an admin with the ID 1']}))
            reset_mocks()
            
        with self.subTest('third EXCEPT block'):
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('second IF block'):
            mock_repo.update.return_value = {'is_active': True}, False
            result = self.facade.deactivate_administrator(1)
            self.assertEqual(result, (500, {'errors': ['Unexpected failure occured.']}))
            reset_mocks()



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
            self.assertIn('Example failure', result[1]['errors'][1])
    
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
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = ({'Success': True}, True)
        
        with self.subTest('Airline not found'):
            mock_repo.update.side_effect = RepoErrors.FetchError()
            result = self.facade.update_airline(name='name', country_id=1)
            self.assertEqual(
                result,
                (404, {'errors': ['Airline not found.']})
            )
            reset_mocks()
            
        with self.subTest('Validation errors'):
            mock_repo.update.side_effect = ValueError('Some error')
            result = self.facade.update_airline(name='name', country_id=1)
            self.assertEqual(
                result,
                (400, {'errors': ['Error while applying request data.', 'Some error']})
            )
            reset_mocks()
            
        with self.subTest('Unexpected exception'):
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.update_airline(name='name', country_id=1)
            self.assertEqual(
                result,
                (500, {'errors': ["The server encountered an unexpected error.", 'Some error']})
            )
            reset_mocks()
    
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
            (200, {'data': {'success': True}})
        )
        mock_repo.add.assert_called_with(
            DBTables.FLIGHT,
            airline_id=1,
            origin_country_id=1,
            destination_country_id=1,
            departure_datetime=time1,
            arrival_datetime=time2,
            total_seats=1
        )
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_flight_errors(self, mock_repo):
        time1 = datetime.now()
        time2 = time1 + timedelta(days=1)
        
        def reset_mocks():
            mock_repo.add.reset_mock(return_value=True, side_effect=True)
            mock_repo.add.return_value = ({'Success': True}, True)
        
        with self.subTest('Validation errors'):
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_flight(1, 1, time1, time2, 1)
            self.assertEqual(
                result,
                (400, {'errors': ['Error while applying request data.', 'Some error']})
            )
            reset_mocks()
    
        with self.subTest('Unexpected exception'):
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_flight(1, 1, time1, time2, 1)
            self.assertEqual(
                result,
                (500, {'errors': ["The server encountered an unexpected error.", 'Some error']})
            )
            reset_mocks()
            
        with self.subTest('Failed addition'):
            mock_repo.add.return_value = ({'Success': False}, False)
            result = self.facade.add_flight(1, 1, time1, time2, 1)
            self.assertEqual(
                result, 
                (400, {'errors': {'Success': False}})
            )
            
            
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
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'airline': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'success': True}, True

        with self.subTest('ID out of bounds'):
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException()
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (400, {'errors': ["Flight ID must be greater than 0."]})
            )
            reset_mocks()
            
        with self.subTest('Bad type/value of '):
            mock_repo.get_by_id.side_effect = ValueError('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (400, {'errors': ["Some error"]})
            )
            reset_mocks()

        with self.subTest('Flight not found'):
            mock_repo.get_by_id.return_value = {}
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (404, {'errors': [f'Could not find flight with ID 1']})
            )
            reset_mocks()

        with self.subTest('Flight owned by different airline'):
            mock_repo.get_by_id.return_value = {'airline': 2}
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (403, {'errors': ['You do not own this flight and cannot update it.']})
            )
            reset_mocks()

        with self.subTest("Repo can't find flight"):
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (404, {'errors': [f'Could not find flight with ID 1']})
            )
            reset_mocks()

        with self.subTest('Validation error with updated fields'):
            mock_repo.update.side_effect = ValueError('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (400, {'errors': ['Error while applying request data.', 'Some error']})
            )
            reset_mocks()

        with self.subTest('Unexpected error'):
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (500, {'errors': ["The server encountered an unexpected error.", 'Some error']})
            )
            reset_mocks()
    
        with self.subTest('Update failure'):
            mock_repo.update.return_value = (['Some error'], False)
            result = self.facade.update_flight(1, total_seats=1)
            self.assertEqual(
                result,
                (400, {'errors': ['Some error']})
            )
            reset_mocks()
    
    @patch('FlightsApi.facades.facades.R')
    def test_cancel_flight_success(self, mock_repo):
        mock_repo.get_by_id.return_value = {'airline': 1}
        mock_repo.update.return_value = ({'is_canceled': True}, True)
        
        result = self.facade.cancel_flight(1)
        
        self.assertEqual(
            result,
            (200, {'data': {'is_canceled': True}})
        )
        mock_repo.get_by_id.assert_called_with(DBTables.FLIGHT, 1)
        mock_repo.update.assert_called_with(DBTables.FLIGHT, id=1, is_canceled=True)
    
    @patch('FlightsApi.facades.facades.R')
    def test_cancel_flight_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'airline': 1}
            
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = ({'is_canceled': True}, True)
            
        with self.subTest('Flight ID out of bounds'):
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException("Some error")
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (400, {'errors': ['Some error']}))
            reset_mocks()
        
        with self.subTest('Get flight - unexpected exception'):
            mock_repo.get_by_id.side_effect = Exception('Some error')
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (500, {'errors': ["The server encountered an unexpected error.", 'Some error']}))
            reset_mocks()
            
        with self.subTest('Flight not found'):
            mock_repo.get_by_id.return_value = {}
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (404, {'errors': ['Flight not found.']}))
            reset_mocks()
            
        with self.subTest('Flight owned by other airline'):
            mock_repo.get_by_id.return_value = {'airline': 2}
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (403, {'errors': ['You cannot modify this flight since it belongs to a different airline.']}))
            reset_mocks()
    
        with self.subTest('Flight not found in repo.update()'):
            mock_repo.update.side_effect = RepoErrors.FetchError
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (404, {'errors': ['Flight not found.']}))
            reset_mocks()
            
        with self.subTest('Validation error on some updated field'):
            mock_repo.update.side_effect = TypeError('Some error')
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('Unexpected exception on update'):
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('Failed update'):
            mock_repo.update.return_value = ({'is_canceled': False}, False)
            result = self.facade.cancel_flight(1)
            self.assertEqual(result, (500, {'errors': ['Something went wrong when cancelling this flight.', "{'is_canceled': False}"]}))
            reset_mocks()
    

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
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'success': True}, True
            
        with self.subTest('Customer not found'):
            mock_repo.update.side_effect = RepoErrors.FetchError('Some error')
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result, (404, {'errors': ["Could not find a customer with the id '1'"]}))
            reset_mocks()
            
        with self.subTest('Validation error'):
            mock_repo.update.side_effect = TypeError('Some error')
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('Unexpected exception'):
            mock_repo.update.side_effect = Exception('Some error')
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', "Some error"]}))
            reset_mocks()
            
        with self.subTest('Failed update'):
            mock_repo.update.return_value = {'success': False}, False
            result = self.facade.update_customer(first_name='first_name')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', {'success': False}]}))
            reset_mocks()
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_ticket_success(self, mock_repo):
        mock_repo.is_flight_bookable.return_value = True, ''
        mock_repo.add.return_value = {'success': True}, True
        
        result = self.facade.add_ticket(1, 2)
        
        self.assertEqual(result, (200, {'data': {'success': True}}))
        mock_repo.is_flight_bookable.assert_called_with(1, 2)
        mock_repo.add.assert_called_with(DBTables.TICKET, flight_id=1, customer_id=1, seat_count=2)
    
    @patch('FlightsApi.facades.facades.R')
    def test_add_ticket_errors(self, mock_repo):
        def reset_mocks():
            mock_repo.is_flight_bookable.reset_mock(return_value=True, side_effect=True)
            mock_repo.is_flight_bookable.return_value = True, ''
            
            mock_repo.add.reset_mock(return_value=True, side_effect=True)
            mock_repo.add.return_value = {'success': True}, True
    
        with self.subTest('Flight not bookable'):
            mock_repo.is_flight_bookable.return_value = False, 'some reason'
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result, (409, {'errors': [f'Cannot book flight because some reason.']}))
            reset_mocks()
    
        with self.subTest('Value error'):
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
    
        with self.subTest('Unexpected Exception'):
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result, (500, {'errors': ["The server encountered an unexpected error.", 'Some error']}))
            reset_mocks()
    
        with self.subTest('Failed addition'):
            mock_repo.add.return_value = {'success': False}, False
            result = self.facade.add_ticket(1, 2)
            self.assertEqual(result, (400, {'errors': {'success': False}}))
            reset_mocks()
    
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
            mock_repo.get_by_id.reset_mock(return_value=True, side_effect=True)
            mock_repo.get_by_id.return_value = {'customer': 1}
            mock_repo.update.reset_mock(return_value=True, side_effect=True)
            mock_repo.update.return_value = {'is_canceled': True}, True
            
        with self.subTest('ID out of bounds'):
            mock_repo.get_by_id.side_effect = RepoErrors.OutOfBoundsException('Some error')
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result, (400, {'errors': ['Some error']}))
            reset_mocks()
            
        with self.subTest('Unexpected error in get_by_id'):
            mock_repo.get_by_id.side_effect = Exception('Some error')
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result, (500, {'errors': ["The server encountered an unexpected error.", 'Some error']}))
            reset_mocks()
            
        with self.subTest('Ticket not found'):
            mock_repo.get_by_id.return_value = {}
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result, (404, {'errors': ['Ticket not found.']}))
            reset_mocks()
            
        with self.subTest('Ticket not owned by user'):
            mock_repo.get_by_id.return_value = {'customer': 2}
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result, (403, {'errors': ['You cannot modify this ticket since it belongs to a different customer.']}))
            reset_mocks()
            
        with self.subTest('Ticket not found in update'):
            mock_repo.update.side_effect = RepoErrors.FetchError()
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result, (404, {'errors': ['Ticket not found.']}))
            reset_mocks()
            
        with self.subTest('Value error in update'):
            mock_repo.update.side_effect = ValueError('Some error')
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
            
        with self.subTest("Ticket wasn't updated"):
            mock_repo.update.return_value = {'is_canceled': False}, False
            result = self.facade.cancel_ticket(1)
            self.assertEqual(result, (500, {'errors': ['Something went wrong when cancelling this ticket.', {'is_canceled': False}]}))
            reset_mocks()
    

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
        self.assertEqual(result, (200, {'data': {'customer': {'id': 1}, 'user': {'id': 1}}}))
        
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
        with self.subTest('first EXCEPT block'):
            mock_repo.add.side_effect = ValueError('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('second EXCEPT block'):
            mock_repo.add.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        with self.subTest('first IF block'):
            mock_repo.add.return_value = ({'SomeError': ['error']}, False)
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, { 'errors': {'SomeError': ['error']} }))
            reset_mocks()
            
        # Adding user to group
        with self.subTest('third EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.EntityNotFoundException
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': ['User ID 1 not found.']}))
            reset_mocks()
            
        with self.subTest('fourth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = RepoErrors.UserAlreadyInGroupException
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (409, {'errors': ['User ID 1 is already assigned to a role.']}))
            reset_mocks()
        
        with self.subTest('fifth EXCEPT block'):
            mock_repo.assign_group_to_user.side_effect = Exception('Some error')
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # Airline creation
        with self.subTest('sixth except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ValueError('Some value error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': ['Error while applying request data.', 'Some value error']}))
            reset_mocks()
            
        with self.subTest('seventh except block'):
            mock_repo.add.side_effect = [({'id': 1}, True), Exception('Some error')]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (500, {'errors': ['The server encountered an unexpected error.', 'Some error']}))
            reset_mocks()
            
        # Airline result verification
        with self.subTest('second IF block'):
            mock_repo.add.side_effect = [({'id': 1}, True), ({'id': 1}, False)]
            result = self.facade.add_customer('username', 'password', 'email', 'first_name', 'last_name', 'address', 'phone_number')
            self.assertEqual(result, (400, {'errors': {'id': 1}}))
            reset_mocks()
    
    