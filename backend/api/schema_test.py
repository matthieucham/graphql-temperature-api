"""Unit tests for schema.py"""
from decimal import Decimal
import json
import pytest
from unittest.mock import MagicMock, patch
from graphene_django.utils.testing import graphql_query
from django.utils import timezone

from api.models import TemperatureModel


# Constant test data
CURRENT_TEMPERATURE = TemperatureModel(
    value=Decimal(19.12345678),
    timestamp=timezone.datetime.fromisoformat("2022-02-15T12:00:00+00:00"),
)
STATS_OUTPUT = {"value__min": Decimal(-18.44367841), "value__max": Decimal(32.08444412)}

# Pytest fixtures
@pytest.fixture
def client_query(client):
    """Test client to perform graphql queries."""

    def func(*args, **kwargs):
        return graphql_query(
            *args, **kwargs, client=client, graphql_url="http://localhost/graphql"
        )

    return func


@pytest.fixture
def mock_manager():
    """Mock the TemperatureModel db manager."""
    mock = MagicMock(spec=TemperatureModel.objects)
    mock.all.return_value = mock
    # emulate required functions in order to return constant test data
    # current temperature
    mock.order_by.return_value = mock
    mock.first.return_value = CURRENT_TEMPERATURE
    # statistics
    mock.filter.return_value = mock
    mock.aggregate.return_value = STATS_OUTPUT
    yield mock


def test_current_temperature(client_query, mock_manager):
    with patch(
        "api.schema.TemperatureModel.objects",
        mock_manager,
    ):
        response = client_query(
            """
            query {
                currentTemperature {
                    timestamp
                    value
                }
            }
            """
        )

        content = json.loads(response.content)
        assert "errors" not in content
        assert "value" in content["data"]["currentTemperature"]
        assert "timestamp" in content["data"]["currentTemperature"]
        assert content["data"]["currentTemperature"]["value"] == str(
            CURRENT_TEMPERATURE.value
        )
        assert (
            timezone.datetime.fromisoformat(
                content["data"]["currentTemperature"]["timestamp"]
            )
            == CURRENT_TEMPERATURE.timestamp
        )


@pytest.mark.parametrize(
    "after,before",
    [
        ("2020-12-06T12:00:00+00:00", None),
        (None, "2020-12-07T12:00:00+00:00"),
        ("2020-12-06T12:00:00+00:00", "2020-12-07T12:00:00+00:00"),
        (None, None),
    ],
)
def test_temperature_statistics(client_query, mock_manager, after, before):
    with patch(
        "api.schema.TemperatureModel.objects",
        mock_manager,
    ):
        response = client_query(
            """
            query($after:DateTime, $before:DateTime) {
                temperatureStatistics(after:$after, before:$before) {
                    min
                    max
                }
            }
            """,
            variables={"after": after, "before": before},
        )

        content = json.loads(response.content)
        assert "errors" not in content
        assert "min" in content["data"]["temperatureStatistics"]
        assert "max" in content["data"]["temperatureStatistics"]
        assert content["data"]["temperatureStatistics"]["min"] == str(
            STATS_OUTPUT["value__min"]
        )
        assert content["data"]["temperatureStatistics"]["max"] == str(
            STATS_OUTPUT["value__max"]
        )
