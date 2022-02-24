from cgi import test
from decimal import Decimal
from typing import List, Tuple
import pytest
from django.utils import timezone
from graphene_django.utils.testing import graphql_query

from api.models import Temperature


SAMPLE = [
    Temperature(
        value=item.get("value"),
        timestamp=timezone.datetime.fromisoformat(item.get("timestamp")),
    )
    for item in [
        {"value": "20.0", "timestamp": "2022-02-01T12:00:00+00:00"},
        {"value": "18.5", "timestamp": "2022-02-01T13:00:00+00:00"},
        {"value": "10.0", "timestamp": "2022-02-01T14:00:00+00:00"},
        {"value": "-5.5", "timestamp": "2022-02-01T15:00:00+00:00"},
    ]
]
SAMPLE_CURRENT_TEMP = max(SAMPLE, key=lambda tm: tm.timestamp)
SAMPLE_MIN = min(SAMPLE, key=lambda tm: tm.value).value
SAMPLE_MAX = max(SAMPLE, key=lambda tm: tm.value).value


@pytest.fixture
def client_query(client):
    """Test client to perform graphql queries."""

    def func(*args, **kwargs):
        return graphql_query(
            *args, **kwargs, client=client, graphql_url="http://localhost/graphql"
        )

    return func


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        Temperature.objects.bulk_create(SAMPLE)
