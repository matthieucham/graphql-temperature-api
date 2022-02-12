"""Consume the temperatures feed."""
from typing import Iterable
import websockets
import asyncio
import json
from django.utils import timezone
from asgiref.sync import sync_to_async


from django.core.management.base import BaseCommand, CommandError
from backend.settings import FEED_URI
from api.models import TemperatureModel


def persist_batch(batch: Iterable[TemperatureModel]) -> None:
    """Persist the batch in db."""
    TemperatureModel.objects.bulk_create(batch)


async def capture_data(batch_size: int):
    """Read from the feed."""
    start = {"type": "start", "payload": {"query": "subscription { temperature }"}}
    batch = list()
    async with websockets.connect(FEED_URI, subprotocols=["graphql-ws"]) as websocket:
        await websocket.send(json.dumps(start))
        while True:
            data = await websocket.recv()
            received = json.loads(data)
            print(received)
            batch.append(
                TemperatureModel(
                    timestamp=timezone.now(),
                    value=received["payload"]["data"]["temperature"],
                )
            )
            if len(batch) >= batch_size:
                await sync_to_async(persist_batch)(batch)
                batch = list()


class Command(BaseCommand):
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
