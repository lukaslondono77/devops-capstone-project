"""
Test cases for Account Model

"""
import logging
import unittest
import os
from service import app
from service.models import Account, DataValidationError, db, PersistentBase, logger
from tests.factories import AccountFactory
import datetime
from flask import Flask

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5433/postgres"
)


######################################################################
#  Account   M O D E L   T E S T   C A S E S
######################################################################
class TestAccount(unittest.TestCase):
    """Test Cases for Account Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Account.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_persistent_base_init(self):
        """Test PersistentBase initialization"""
        base = PersistentBase()
        self.assertIsNone(base.id)

    def test_persistent_base_create(self):
        """Test PersistentBase create method"""
        account = AccountFactory()
        # Test create with logging
        with self.assertLogs(logger, level='INFO') as log:
            account.create()
            self.assertIn(f"Creating {account.name}", log.output[0])
        self.assertIsNotNone(account.id)

    def test_persistent_base_update(self):
        """Test PersistentBase update method"""
        account = AccountFactory()
        account.create()
        # Test update with logging
        with self.assertLogs(logger, level='INFO') as log:
            account.update()
            self.assertIn(f"Updating {account.name}", log.output[0])

    def test_persistent_base_delete(self):
        """Test PersistentBase delete method"""
        account = AccountFactory()
        account.create()
        # Test delete with logging
        with self.assertLogs(logger, level='INFO') as log:
            account.delete()
            self.assertIn(f"Deleting {account.name}", log.output[0])
        # Verify account is deleted
        self.assertIsNone(Account.find(account.id))

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_account(self):
        """It should Create an Account and assert that it exists"""
        fake_account = AccountFactory()
        # pylint: disable=unexpected-keyword-arg
        account = Account(
            name=fake_account.name,
            email=fake_account.email,
            address=fake_account.address,
            phone_number=fake_account.phone_number,
            date_joined=fake_account.date_joined,
        )
        self.assertIsNotNone(account)
        self.assertEqual(account.id, None)
        self.assertEqual(account.name, fake_account.name)
        self.assertEqual(account.email, fake_account.email)
        self.assertEqual(account.address, fake_account.address)
        self.assertEqual(account.phone_number, fake_account.phone_number)
        self.assertEqual(account.date_joined, fake_account.date_joined)

    def test_add_a_account(self):
        """It should Create an account and add it to the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = AccountFactory()
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

    def test_read_account(self):
        """It should Read an account"""
        account = AccountFactory()
        account.create()

        # Read it back
        found_account = Account.find(account.id)
        self.assertEqual(found_account.id, account.id)
        self.assertEqual(found_account.name, account.name)
        self.assertEqual(found_account.email, account.email)
        self.assertEqual(found_account.address, account.address)
        self.assertEqual(found_account.phone_number, account.phone_number)
        self.assertEqual(found_account.date_joined, account.date_joined)

    def test_update_account(self):
        """It should Update an account"""
        account = AccountFactory(email="advent@change.me")
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        self.assertEqual(account.email, "advent@change.me")

        # Fetch it back
        account = Account.find(account.id)
        account.email = "XYZZY@plugh.com"
        account.update()

        # Fetch it back again
        account = Account.find(account.id)
        self.assertEqual(account.email, "XYZZY@plugh.com")

    def test_delete_an_account(self):
        """It should Delete an account from the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = AccountFactory()
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        account.delete()
        accounts = Account.all()
        self.assertEqual(len(accounts), 0)

    def test_list_all_accounts(self):
        """It should List all Accounts in the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        for account in AccountFactory.create_batch(5):
            account.create()
        # Assert that there are not 5 accounts in the database
        accounts = Account.all()
        self.assertEqual(len(accounts), 5)

    def test_find_by_name(self):
        """It should Find an Account by name"""
        # Create test accounts
        account1 = AccountFactory()
        account2 = AccountFactory()
        account3 = AccountFactory()
        account1.name = "John"
        account2.name = "John"
        account3.name = "Jane"
        account1.create()
        account2.create()
        account3.create()

        # Test finding accounts by name
        accounts = Account.find_by_name("John").all()
        self.assertEqual(len(accounts), 2)
        self.assertEqual(accounts[0].name, "John")
        self.assertEqual(accounts[1].name, "John")

        # Test finding non-existent name
        accounts = Account.find_by_name("Bob").all()
        self.assertEqual(len(accounts), 0)

        # Test finding with empty string
        accounts = Account.find_by_name("").all()
        self.assertEqual(len(accounts), 0)

    def test_serialize_an_account(self):
        """It should Serialize an account"""
        account = AccountFactory()
        serial_account = account.serialize()
        self.assertEqual(serial_account["id"], account.id)
        self.assertEqual(serial_account["name"], account.name)
        self.assertEqual(serial_account["email"], account.email)
        self.assertEqual(serial_account["address"], account.address)
        self.assertEqual(serial_account["phone_number"], account.phone_number)
        self.assertEqual(serial_account["date_joined"], str(account.date_joined))

    def test_deserialize_an_account(self):
        """It should Deserialize an account"""
        account = AccountFactory()
        account.create()
        serial_account = account.serialize()
        new_account = Account()
        new_account.deserialize(serial_account)
        self.assertEqual(new_account.name, account.name)
        self.assertEqual(new_account.email, account.email)
        self.assertEqual(new_account.address, account.address)
        self.assertEqual(new_account.phone_number, account.phone_number)
        self.assertEqual(new_account.date_joined, account.date_joined)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an account with a KeyError"""
        account = Account()
        self.assertRaises(DataValidationError, account.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an account with a TypeError"""
        account = Account()
        # Test with non-dict data
        with self.assertRaises(DataValidationError) as context:
            account.deserialize("not a dict")
        self.assertIn("Invalid Account: body of request contained bad or no data", str(context.exception))
        
        # Test with None
        with self.assertRaises(DataValidationError) as context:
            account.deserialize(None)
        self.assertIn("Invalid Account: body of request contained bad or no data", str(context.exception))

    def test_deserialize_type_error(self):
        acc = Account()
        with self.assertRaises(DataValidationError):
            acc.deserialize("not-a-dict")

    def test_deserialize_empty_dict(self):
        acc = Account()
        with self.assertRaises(DataValidationError):
            acc.deserialize({})

    def test_deserialize_missing_field(self):
        acc = Account()
        # Missing required fields: email, address
        payload = {'name': 'Test'}
        with self.assertRaises(DataValidationError) as cm:
            acc.deserialize(payload)
        self.assertIn('missing', str(cm.exception).lower())

    def test_deserialize_invalid_date(self):
        acc = Account()
        payload = {
            'name': 'Test',
            'email': 't@e.com',
            'address': 'x',
            'phone_number': '123',
            'date_joined': 'not-a-date'
        }
        with self.assertRaises(DataValidationError):
            acc.deserialize(payload)

    def test_serialize_repr_and_find_by_name(self):
        # Create a minimal Flask app to initialize the in-memory DB
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        Account.init_db(app)

        with app.app_context():
            # Create two accounts
            a1 = Account(name='Alice', email='a@a.com', address='Addr', phone_number='000', date_joined=datetime.date.today())
            a2 = Account(name='Bob',   email='b@b.com', address='Addr', phone_number='111', date_joined=datetime.date.today())
            db.session.add_all([a1, a2])
            db.session.commit()
            # serialize()
            data = a1.serialize()
            self.assertEqual(data['name'], 'Alice')
            # __repr__()
            rep = repr(a1)
            self.assertTrue(rep.startswith('<Account '))
            # find_by_name()
            results = Account.find_by_name('Alice').all()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, 'Alice')

if __name__ == '__main__':  # pragma: no cover
    unittest.main()
