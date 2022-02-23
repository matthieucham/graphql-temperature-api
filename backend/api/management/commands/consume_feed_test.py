from unittest.mock import MagicMock, patch

from api.management.commands.consume_feed import process_reading


def test_process_reading_with_persist():
    """Test that process_reading call the persistence method when the batch is full"""
    # Given
    batch = [MagicMock()]
    batch_size = len(batch) + 1
    received = {"payload": {"data": {"temperature": 20.5}}}
    # When
    with patch(
        "api.management.commands.consume_feed.Temperature.objects.bulk_create"
    ) as mock_bulk_create:
        next_batch = process_reading(received, batch, batch_size)
        # Then
        mock_bulk_create.assert_called_once_with(batch)
        assert len(next_batch) == 0


def test_process_reading_without_persist():
    """Test that process_reading don't call the persistence method when the batch is not full"""
    # Given
    batch = [MagicMock()]
    batch_size = len(batch) + 2
    current_size = len(batch)
    received = {"payload": {"data": {"temperature": 20.5}}}
    # When
    with patch(
        "api.management.commands.consume_feed.Temperature.objects.bulk_create"
    ) as mock_bulk_create:
        next_batch = process_reading(received, batch, batch_size)
        # Then
        mock_bulk_create.assert_not_called()
        assert len(next_batch) == current_size + 1
