from unittest.mock import MagicMock, patch

from api.management.commands.consume_feed import process_reading
from api.models import ReadConfig


def test_process_reading_with_persist():
    """Test that process_reading call the persistence method when the batch is full"""
    # Given
    received = {"payload": {"data": {"temperature": 20.5}}}
    # When
    with patch(
        "api.management.commands.consume_feed.Temperature.objects.create"
    ) as mock_create, patch(
        "api.management.commands.consume_feed.ReadConfig.objects.get",
        return_value=ReadConfig(config_key="status", config_value="on"),
    ):
        process_reading(received)
        # Then
        mock_create.assert_called_once()


def test_process_reading_without_persist():
    """Test that process_reading don't call the persistence method when the batch is not full"""
    # Given
    received = {"payload": {"data": {"temperature": 20.5}}}
    # When
    with patch(
        "api.management.commands.consume_feed.Temperature.objects.create"
    ) as mock_create, patch(
        "api.management.commands.consume_feed.ReadConfig.objects.get",
        return_value=ReadConfig(config_key="status", config_value="off"),
    ):
        process_reading(received)
        # Then
        mock_create.assert_not_called()
