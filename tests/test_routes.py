######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestCustomer API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch, MagicMock
from wsgi import app
from service.common import status
from service.models import db, Customer, DataValidationError
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/customers"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Customer REST API Service")

    def _create_customers(self, count: int = 1) -> list:
        """Factory method to create customers in bulk"""
        customers = []
        for _ in range(count):
            test_customer = CustomerFactory()
            response = self.client.post(BASE_URL, json=test_customer.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test customer",
            )
            new_customer = response.get_json()
            test_customer.id = new_customer["id"]
            customers.append(test_customer)
        return customers

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_customer(self):
        """It should Create a new Customer"""
        test_customer = CustomerFactory()
        logging.debug("Test Customer: %s", test_customer.serialize())
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_customer = response.get_json()
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["phone_number"], test_customer.phone_number)

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_customer = response.get_json()
        self.assertEqual(new_customer["name"], test_customer.name)
        self.assertEqual(new_customer["email"], test_customer.email)
        self.assertEqual(new_customer["address"], test_customer.address)
        self.assertEqual(new_customer["phone_number"], test_customer.phone_number)

    def test_get_customer_list(self):
        """It should Get a list of Customers"""
        self._create_customers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

        # ----------------------------------------------------------

    # TEST READ
    # ----------------------------------------------------------
    def test_get_customer(self):
        """It should Get a single Customer"""
        # get the id of a customer
        test_customer = self._create_customers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_customer.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_customer.name)

    def test_get_customer_not_found(self):
        """It should not Get a Customer thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_customer(self):
        """It should Update an existing Customer"""
        # create a customer to update
        test_customer = CustomerFactory()
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the customer
        new_customer = response.get_json()
        new_customer["name"] = "Updated Name"
        new_customer["email"] = "updated_email@example.com"
        new_customer["phone_number"] = "123-456-7890"
        new_customer["address"] = "123 Updated Address"
        response = self.client.put(
            f"{BASE_URL}/{new_customer['id']}", json=new_customer
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_customer = response.get_json()
        self.assertEqual(updated_customer["name"], "Updated Name")
        self.assertEqual(updated_customer["email"], "updated_email@example.com")
        self.assertEqual(updated_customer["phone_number"], "123-456-7890")
        self.assertEqual(updated_customer["address"], "123 Updated Address")


class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a customer id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_customer_no_data(self):
        """It should not Create a Customer with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_no_content_type(self):
        """It should not Create a Customer with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_wrong_content_type(self):
        """It should not Create a Customer with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_customer_bad_email(self):
        """It should not Create a Customer with bad phone_number data"""
        test_customer = CustomerFactory()
        logging.debug(test_customer)
        test_customer.name = ""
        test_customer.phone_number = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        response = self.client.post(BASE_URL, json=test_customer.serialize())
        print(response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  T E S T   M O C K S
    ######################################################################

    @patch("service.routes.Customer.find_by_name")
    def test_bad_request_name(self, bad_request_mock):
        """It should return a Bad Request error from Find By Name"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="name=fido")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.routes.Customer.find_by_name")
    def test_mock_search_data_name(self, customer_find_mock):
        """It should showing how to mock data"""
        customer_find_mock.return_value = [
            MagicMock(serialize=lambda: {"name": "fido"})
        ]
        response = self.client.get(BASE_URL, query_string="name=fido")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("service.routes.Customer.find_by_email")
    def test_bad_request_email(self, bad_request_mock):
        """It should return a Bad Request error from Find By email"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="email=test@nyu.edu")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.routes.Customer.find_by_email")
    def test_mock_search_data_email(self, customer_find_mock):
        """It should showing how to mock data"""
        customer_find_mock.return_value = [
            MagicMock(serialize=lambda: {"email": "test@nyu.edu"})
        ]
        response = self.client.get(BASE_URL, query_string="email=test@nyu.edu")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("service.routes.Customer.find_by_phone_number")
    def test_bad_request_phone_number(self, bad_request_mock):
        """It should return a Bad Request error from Find By phone_number"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="phone_number=123-456-78910")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.routes.Customer.find_by_phone_number")
    def test_mock_search_data_phone_number(self, customer_find_mock):
        """It should showing how to mock data"""
        customer_find_mock.return_value = [
            MagicMock(serialize=lambda: {"phone_number": "123-456-78910"})
        ]
        response = self.client.get(BASE_URL, query_string="phone_number=123-456-78910")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("service.routes.Customer.find_by_address")
    def test_bad_request_address(self, bad_request_mock):
        """It should return a Bad Request error from Find By address"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="address=NYC, NY")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.routes.Customer.find_by_address")
    def test_mock_search_data_address(self, customer_find_mock):
        """It should showing how to mock data"""
        customer_find_mock.return_value = [
            MagicMock(serialize=lambda: {"address": "NYC, NY"})
        ]
        response = self.client.get(BASE_URL, query_string="address=NYC, NY")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
