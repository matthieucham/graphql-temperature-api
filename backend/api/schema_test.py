"""Unit tests for schema.py"""
from decimal import Decimal
import json
from django.forms import ValidationError
import pytest
from unittest.mock import MagicMock, patch
from graphene_django.utils.testing import graphql_query
from django.utils import timezone

from api.models import Temperature, ReadConfig


# Constant test data
CURRENT_TEMPERATURE = Temperature(
    value=Decimal(19.12345678),
    timestamp=timezone.datetime.fromisoformat("2022-02-15T12:00:00+00:00"),
)
STATS_OUTPUT = {"value__min": Decimal(-18.44367841), "value__max": Decimal(32.08444412)}

STATUS_CONFIG = ReadConfig(config_key="status", config_value="on")

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
    """Mock the Temperature db manager."""
    mock = MagicMock(spec=Temperature.objects)
    mock.all.return_value = mock
    # emulate required functions in order to return constant test data
    # current temperature
    mock.order_by.return_value = mock
    mock.first.return_value = CURRENT_TEMPERATURE
    # statistics
    mock.filter.return_value = mock
    mock.aggregate.return_value = STATS_OUTPUT
    yield mock


@pytest.fixture
def mock_config_manager():
    """Mock the ReadConfig db manager."""
    mock = MagicMock(spec=ReadConfig.objects)
    mock.update_or_create.return_value = STATUS_CONFIG, False
    yield mock


@pytest.fixture
def mock_cache():
    """Mock the cache."""
    mock = MagicMock()
    yield mock


def test_current_temperature(client_query, mock_manager):
    with patch(
        "api.schema.Temperature.objects",
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
        "api.schema.Temperature.objects",
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


def test_toggle_feed_on(client_query, mock_config_manager, mock_cache):
    """Test that the db and the cache are updated."""
    with patch(
        "api.schema.ReadConfig.objects",
        mock_config_manager,
    ) as config_manager, patch("api.schema.cache", mock_cache) as cache:
        response = client_query(
            """
            mutation {
                toggleFeed(input: {status: "on"}) {
                    status
                }
            }
            """
        )
        content = json.loads(response.content)
        assert "errors" not in content
        assert "status" in content["data"]["toggleFeed"]
        assert content["data"]["toggleFeed"]["status"] == "on"
        config_manager.update_or_create.assert_called_once_with(
            config_key="status", defaults={"config_value": "on"}
        )
        cache.set.assert_called_once_with("status", "on")


def test_toggle_feed_bad_input(client_query, mock_config_manager, mock_cache):
    """Test that an error is returned."""
    with patch(
        "api.schema.ReadConfig.objects",
        mock_config_manager,
    ) as config_manager, patch("api.schema.cache", mock_cache) as cache:
        response = client_query(
            """
            mutation {
                toggleFeed(input: {status: "ooof"}) {
                    status
                }
            }
            """
        )
        content = json.loads(response.content)
        assert "errors" in content
        config_manager.update_or_create.assert_not_called()
        cache.set.assert_not_called()
