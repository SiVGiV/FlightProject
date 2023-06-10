from django.test import TestCase
from ..repository.repository import Repository, verify_model
from ..repository.errors import FetchError, CreationError, UpdateError, WrongModelType
from ..models import User, Admin, AirlineCompany, Customer


class TestVerifyModel(TestCase):
    def test_model_class(self):
        test_func = verify_model(lambda x: True)
        self.assertTrue(test_func(User))
    
    def test_other_class(self):
        test_func = verify_model(lambda x: True)
        self.assertRaises(WrongModelType, lambda: test_func(int))
    
    def test_non_class(self):
        test_func = verify_model(lambda x: True)
        self.assertRaises(WrongModelType, lambda: test_func(1))


class TestGetById(TestCase):
    def test_get_by_id_success(self):
        user = User.objects.create_user("testUser", "test@a.com")
        customer = Customer.objects.create(
            first_name="testy",
            last_name="testson",
            address="123 test st.",
            phone_number="+972 1231212",
            credit_card_number="1234 1234 1234 1234",
            user=user
        )
        user.save()
        customer.save()
        
        with self.subTest("User by ID"):
            user_from_repo = Repository.get_by_id(User, user.id)
            self.assertEqual(user_from_repo.id, user.id)
        with self.subTest("Customer by ID"):
            customer_from_repo = Repository.get_by_id(Customer, customer.id)
            self.assertEqual(customer_from_repo.id, customer.id)
        
    def test_get_by_id_with_non_existing_id(self):
        self.assertIsNone(Repository.get_by_id(AirlineCompany, 1))
    
    def test_get_by_id_bad_id_type(self):
        self.assertRaises(FetchError, lambda: Repository.get_by_id(User, "jeff"))
    
    def test_get_by_id_bad_id_value(self):
        self.assertRaises(FetchError, lambda: Repository.get_by_id(User, -1))
    
    
class TestGetAll(TestCase):
    def test_get_all_success(self):
        users = []
        with self.subTest("Empty database"):
            self.assertCountEqual(users, Repository.get_all(User))
            
        user1 = User.objects.create_user("testUser1", "test1@a.com", "test1234")
        user1.save()
        users.append(user1)
        with self.subTest("Single entry"):
            self.assertCountEqual(users, Repository.get_all(User))
            self.assertEqual(user1.pk, Repository.get_all(User)[0].pk) # Check content of an entry
            
        user2 = User.objects.create_user("testUser2", "test2@a.com", "test2345")
        user2.save()
        users.append(user2)
        with self.subTest("Multiple Entries"):
            self.assertCountEqual(users, Repository.get_all(User))
    

class TestAdd(TestCase):
    def test_add_success(self):
        user = None
        with self.subTest("User creation"):
            user = Repository.add(User,
                                  username="testUser",
                                  email="test@a.com",
                                  password="test1234")
            self.assertEqual(user.username, "testUser")
        with self.subTest("Customer creation"):
            customer = Repository.add(Customer,
                                      first_name="testy",
                                      last_name="testson",
                                      address="123 test st.",
                                      phone_number="+972 1231212",
                                      credit_card_number="1234 1234 1234 1234",
                                      user=user
            )
            self.assertEqual(customer.first_name, "testy")
            
    def test_bad_data(self):
        with self.subTest("Missing Fields"):
            self.assertRaises(CreationError, lambda: Repository.add(User, email="a@a.com", password="test123"))
        with self.subTest("Wrong field type"):
            self.assertRaises(CreationError, lambda: Repository.add(Admin, first_name="admin", last_name="admin", user="bad field"))


class TestUpdate(TestCase):
    def test_update_success(self):
        user = User.objects.create_user("test", "a@a.com", "1234")
        Repository.update(User, user.id, email="b@b.com")
        updated_user = User.objects.get(pk=user.id)
        self.assertEqual(updated_user.email, "b@b.com")

    def test_update_non_existing_id(self):
        self.assertRaises(FetchError, lambda: Repository.update(User, 1, email="b@b.com"))
        
    def test_update_no_fields(self):
        user = User.objects.create_user("test", "a@a.com", "1234")
        self.assertEqual(user.username, Repository.update(User, user.id).username)
        
    def test_update_attribute_errors(self):
        user = User.objects.create_user("test", "a@a.com", "1234")
        with self.subTest("Non existing attribute"):
            self.assertRaises(UpdateError, lambda: Repository.update(User, user.id, fakefield="fakevalue"))
        with self.subTest("Bad type"):
            self.assertRaises(UpdateError, lambda: Repository.update(User, user.id, is_active="not bool"))


class TestAddAll(TestCase):
    def test_add_all_success(self):
        new_rows = [
            {'username': "test1", 'email': "a@a.com", 'password': "test1"},
            {'username': "test2", 'email': "b@b.com", 'password': "test2"}
        ]
        self.assertEqual(2, len(Repository.add_all(User, new_rows)))
    
    def test_add_all_empty(self):
        self.assertEqual(0, len(Repository.add_all(User, [])))


class TestRemove(TestCase):
    def test_remove_success(self):
        user = User.objects.create_user("test1", "a@a.com", "1234")
        id = user.id
        Repository.remove(User, id)
        self.assertEqual(0, len(User.objects.filter(pk=id)))
        
    def test_remove_non_existing(self):
        try:
            Repository.remove(User, 1)
        except Exception as e:
            self.fail("Repository.remove() did not complete!")


