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
Test cases for Customer Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Customer, DataValidationError, db
from .factories import CustomerFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


class TestCaseBase(TestCase):
    """Base Test Case for common setup"""

    # pylint: disable=duplicate-code
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


######################################################################
#  Customer   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCustomer(TestCaseBase):
    """Test Cases for Customer Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Customer).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_customer_model(self):
        """It should create a Customer"""
        resource = CustomerFactory()
        resource.create()
        self.assertIsNotNone(resource.id)
        found = Customer.all()
        self.assertEqual(len(found), 1)
        data = Customer.find(resource.id)
        self.assertEqual(data.name, resource.name)
        self.assertEqual(data.phone_number, resource.phone_number)
        self.assertEqual(data.email, resource.email)
        self.assertEqual(data.address, resource.address)

    # Todo: Add your test cases here...

    def test_read_a_customer(self):
        """It should Read a Customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        self.assertIsNotNone(customer.id)
        # Fetch it back
        found_customer = Customer.find(customer.id)
        self.assertEqual(found_customer.id, customer.id)
        self.assertEqual(found_customer.name, customer.name)
        self.assertEqual(found_customer.email, customer.email)
        self.assertEqual(found_customer.phone_number, customer.phone_number)
        self.assertEqual(found_customer.address, customer.address)

    def test_update_a_customer(self):
        """It should Update a Customer"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        customer.create()
        logging.debug(customer)
        self.assertIsNotNone(customer.id)
        # Change it an save it
        customer.name = "k9"
        original_id = customer.id
        customer.update()
        self.assertEqual(customer.id, original_id)
        self.assertEqual(customer.name, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        customers = Customer.all()
        self.assertEqual(len(customers), 1)
        self.assertEqual(customers[0].id, original_id)
        self.assertEqual(customers[0].name, "k9")

    def test_update_no_id(self):
        """It should not Update a Customer with no id"""
        customer = CustomerFactory()
        logging.debug(customer)
        customer.id = None
        self.assertRaises(DataValidationError, customer.update)

    def test_delete_a_customer(self):
        """It should Delete a Customer"""
        customer = CustomerFactory()
        customer.create()
        self.assertEqual(len(Customer.all()), 1)
        # delete the customer and make sure it isn't in the database
        customer.delete()
        self.assertEqual(len(Customer.all()), 0)

    def test_list_all_customers(self):
        """It should List all Customers in the database"""
        customers = Customer.all()
        self.assertEqual(customers, [])
        # Create 5 Customers
        for _ in range(5):
            customer = CustomerFactory()
            customer.create()
        # See if we get back 5 customers
        customers = Customer.all()
        self.assertEqual(len(customers), 5)


class TestExceptionHandlers(TestCaseBase):

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        customer = CustomerFactory()
        self.assertRaises(DataValidationError, customer.delete)
