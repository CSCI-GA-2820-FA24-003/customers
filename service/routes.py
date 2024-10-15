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
Customer Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Customer
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Customer
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""

    return (
        jsonify(
            name="Customer REST API Service",
            version="1.0",
            description=(
                "This is a RESTful service for managing customers. You can list, view, "
                "create, update, and delete customer information."
            ),
            paths={
                "list_customers": {
                    "method": "GET",
                    "url": url_for("list_customers", _external=True),
                },
                "get_customer": {
                    "method": "GET",
                    "url": url_for("get_customers", customer_id=1, _external=True),
                },
                "create_customer": {
                    "method": "POST",
                    "url": url_for("create_customers", _external=True),
                },
                "update_customer": {
                    "method": "PUT",
                    "url": url_for("update_customers", customer_id=1, _external=True),
                },
            },
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/customers", methods=["POST"])
def create_customers():
    """
    Create a Customer
    This endpoint will create a Customer based the data in the body that is posted
    """
    app.logger.info("Request to Create a Customer...")
    check_content_type("application/json")

    customer = Customer()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.deserialize(data)

    # Save the new Customer to the database
    customer.create()
    app.logger.info("Customer with new id [%s] saved!", customer.id)

    # Return the location of the new Customer
    location_url = url_for("get_customers", customer_id=customer.id, _external=True)
    return (
        jsonify(customer.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


@app.route("/customers", methods=["GET"])
def list_customers():
    """Returns all of the Customers"""
    app.logger.info("Request for customer list")

    customers = []

    name = request.args.get("name")
    email = request.args.get("email")
    phone_number = request.args.get("phone_number")
    address = request.args.get("address")

    if name:
        app.logger.info("Find by name: %s", name)
        customers = Customer.find_by_name(name)
    elif email:
        app.logger.info("Find by email: %s", email)
        customers = Customer.find_by_email(email)
    elif phone_number:
        app.logger.info("Find by phone_number: %s", phone_number)
        # create enum from string
        customers = Customer.find_by_phone_number(phone_number)
    elif address:
        app.logger.info("Find by address: %s", address)
        customers = Customer.find_by_address(address)
    else:
        app.logger.info("Find all")
        customers = Customer.all()

    results = [customer.serialize() for customer in customers]
    app.logger.info("Returning %d customers", len(results))
    return jsonify(results), status.HTTP_200_OK


@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customers(customer_id):
    """
    Retrieve a single Customer

    This endpoint will return a Customer based on it's id
    """
    app.logger.info("Request to Retrieve a customer with id [%s]", customer_id)

    # Attempt to find the Customer and abort if not found
    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    app.logger.info("Returning customer: %s", customer.name)
    return jsonify(customer.serialize()), status.HTTP_200_OK


######################################################################
# CREATE A NEW PET
######################################################################


######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route("/customers/<int:customer_id>", methods=["PUT"])
def update_customers(customer_id):
    """
    Update a Customer
    This endpoint will update a Customer based the body that is posted
    """
    app.logger.info("Request to Update a customer with id [%s]", customer_id)
    check_content_type("application/json")

    customer = Customer.find(customer_id)
    if not customer:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Customer with id '{customer_id}' was not found.",
        )

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    customer.deserialize(data)

    customer.update()
    app.logger.info("Customer with id [%s] updated!", customer.id)
    return jsonify(customer.serialize()), status.HTTP_200_OK


def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
