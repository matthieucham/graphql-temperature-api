"""Consume the temperatures feed."""
from typing import Any, Dict, Iterable, List
import websockets
import asyncio
import json
from django.utils import timezone
from asgiref.sync import sync_to_async


from django.core.management.base import BaseCommand, CommandError
from backend.settings import FEED_URI
from api.models import TemperatureModel


# process_reading is isolated from capture_data in order to ease its testing.


def process_reading(
    received: Dict[str, Any], current_batch: List[TemperatureModel], batch_size: int
) -> List[TemperatureModel]:
    """Process an incoming temperature reading: grow the batch and persist eventually.

    Args:
        received (Dict[str,Any]): received reading (json)
        current_batch (List[TemperatureModel]): current batch of TemperatureModel waiting to be stored
        batch_size (int): number of readings to accumulate in each batch.

    Returns:
        List[TemperatureModel]: the batch for the next call.
    """
    current_batch.append(
        TemperatureModel(
            timestamp=timezone.now(),
            value=received["payload"]["data"]["temperature"],
        )
    )
    if len(current_batch) >= batch_size:
        TemperatureModel.objects.bulk_create(current_batch)
        # initiate a new batch
        return list()
    return current_batch


async def capture_data(batch_size: int):  # pragma: no cover
    """Read from the feed."""
    start = {"type": "start", "payload": {"query": "subscription { temperature }"}}
    batch = list()
    async with websockets.connect(FEED_URI, subprotocols=["graphql-ws"]) as websocket:
        await websocket.send(json.dumps(start))
        while True:
            data = await websocket.recv()
            received = json.loads(data)
            print(received)
            batch = await sync_to_async(process_reading)(received, batch, batch_size)


class Command(BaseCommand):  # pragma: no cover
    """Custom command to consume the temperatures feed and store read values in db."""

    help = "Consume the temperatures feed and store read values in db"

    def add_arguments(self, parser):
        """Add a batch_size argument"""
        parser.add_argument(
            "batch_size",
            nargs="?",
            type=int,
            help="Number of values in batches of data to persist.",
            default=10,
        )

    def handle(self, *args, **options):
        """Consume the feed in an infinite loop and persist data by batches."""
        self.stdout.write(f"Launch consumption of temperature feed at {FEED_URI}")

        asyncio.run(capture_data(batch_size=options["batch_size"]))
