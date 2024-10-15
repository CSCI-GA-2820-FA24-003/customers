"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Customer


class CustomerFactory(factory.Factory):
    """Creates fake customers that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Customer

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    email = factory.Faker("email")
    phone_number = factory.Faker("phone_number")
    address = factory.Faker("address")
