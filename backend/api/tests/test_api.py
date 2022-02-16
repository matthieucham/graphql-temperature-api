"""API tests."""

import pytest
import json
from decimal import Decimal
from django.utils import timezone


@pytest.mark.django_db
def test_current_temperature(client_query):
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
    assert Decimal(content["data"]["currentTemperature"]["value"]) == Decimal(-5.5)
    assert timezone.datetime.fromisoformat(
        content["data"]["currentTemperature"]["timestamp"]
    ) == timezone.datetime.fromisoformat("2022-02-01T15:00:00+00:00")


@pytest.mark.django_db
@pytest.mark.parametrize(
    argnames="after, before, expectmin, expectmax",
    argvalues=[
        (
            "2022-02-01T12:30:00+00:00",
            "2022-02-01T14:00:00+00:00",
            Decimal(10),
            Decimal(18.5),
        ),
        ("2022-02-01T14:30:00+00:00", None, Decimal(-5.5), Decimal(-5.5)),
        (None, "2022-02-01T13:00:00+00:00", Decimal(18.5), Decimal(20)),
        (None, None, Decimal(-5.5), Decimal(20)),
    ],
)
def test_temperature_statistics(client_query, after, before, expectmin, expectmax):
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
    assert Decimal(content["data"]["temperatureStatistics"]["min"]) == expectmin
    assert Decimal(content["data"]["temperatureStatistics"]["max"]) == expectmax
