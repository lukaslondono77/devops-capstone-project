# tests/test_account_service.py

import os
import logging
from unittest import TestCase
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app
import unittest
from flask import request

# Import AccountFactory if defined elsewhere
from tests.factories import AccountFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5433/postgres"
)

BASE_URL = "/accounts"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""
        pass

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()
        self.app = app

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        resp = self.client.post(
            "/accounts",
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="text/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_list_accounts(self):
        """Test listing all accounts"""
        # Create some test accounts
        self._create_accounts(3)

        # Send a GET request to list all accounts
        response = self.client.get(BASE_URL)

        # Assert the response status code and content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)  # Adjust based on the number of accounts created

    def test_get_account(self):
        """It should Read a single Account"""
        account = self._create_accounts(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{account.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], account.name)
        self.assertEqual(data["email"], account.email)
        # Add assertions for other fields as needed

    def test_get_account_not_found(self):
        """It should not Read an Account that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_account(self):
        """It should Update an existing Account"""
        # create an Account to update
        test_account = AccountFactory()
        resp = self.client.post(BASE_URL, json=test_account.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the account
        new_account = resp.get_json()
        new_account["name"] = "Something Known"
        resp = self.client.put(f"{BASE_URL}/{new_account['id']}", json=new_account)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_account = resp.get_json()
        self.assertEqual(updated_account["name"], "Something Known")

    def test_delete_account(self):
        """It should Delete an Account"""
        account = self._create_accounts(1)[0]
        resp = self.client.delete(
            f"{BASE_URL}/{account.id}",
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_check_content_type_valid(self):
        """Test check_content_type with valid content type"""
        with self.app.test_request_context(headers={'Content-Type': 'application/json'}):
            from service.routes import check_content_type
            check_content_type('application/json')  # Should not raise an error
            # Ensure the return path is covered
            self.assertEqual(request.headers.get('Content-Type'), 'application/json')

    def test_check_content_type_invalid(self):
        """Test check_content_type with invalid content type"""
        with self.app.test_request_context(headers={'Content-Type': 'text/html'}):
            from service.routes import check_content_type
            with self.assertRaises(Exception):
                check_content_type('application/json')

    def test_method_not_allowed(self):
        """Test method not allowed error handler"""
        # Use a method not allowed on a valid route, e.g., PATCH on /accounts
        response = self.client.patch('/accounts', json={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.get_json()
        self.assertIn('error', data)

    def test_update_account_success(self):
        """Test updating an existing Account"""
        # Create a test account
        test_account = self._create_accounts(1)[0]
        
        # Define the update payload
        update_data = {
            "name": "Updated Name",
            "email": "updated.email@example.com",
            "address": "456 Updated Street",
            "phone_number": "987-654-3210",
            "date_joined": "2023-01-01"
        }
        
        # Call PUT /accounts/<test_account.id> with the update payload
        response = self.client.put(
            f"{BASE_URL}/{test_account.id}",
            json=update_data,
            content_type="application/json"
        )
        
        # Assert status 200 and that the returned JSON reflects the updated fields
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_account = response.get_json()
        self.assertEqual(updated_account["name"], "Updated Name")
        self.assertEqual(updated_account["email"], "updated.email@example.com")
        self.assertEqual(updated_account["address"], "456 Updated Street")
        self.assertEqual(updated_account["phone_number"], "987-654-3210")
        self.assertEqual(updated_account["date_joined"], "2023-01-01")

    def test_update_account_not_found(self):
        """Test updating a non-existent Account"""
        # Call PUT /accounts/9999 (or any ID that doesn't exist)
        response = self.client.put(
            f"{BASE_URL}/9999",
            json={"name": "New Name", "email": "new.email@example.com", "address": "123 New Street"},
            content_type="application/json"
        )
        
        # Assert status 404 and the correct error message
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("Account with id [9999] could not be found.", data["message"])

if __name__ == '__main__':  # pragma: no cover
    unittest.main()

