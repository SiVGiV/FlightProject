from unittest import TestCase
from unittest.mock import MagicMock, patch

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


