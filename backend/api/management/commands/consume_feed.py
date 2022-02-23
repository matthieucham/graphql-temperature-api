"""Consume the temperatures feed."""
from typing import Any, Dict, Iterable, List
import websockets
import asyncio
import json
from django.utils import timezone
from asgiref.sync import sync_to_async


from django.core.management.base import BaseCommand
from backend.settings import FEED_URI
from api.models import Temperature, ReadConfig


# process_reading is isolated from capture_data in order to ease its testing.


def process_reading(received: Dict[str, Any]) -> None:
    """Process an incoming temperature reading and persist.

    Args:
        received (Dict[str,Any]): received reading (json)
    """
    # Check if reading is on before persisting
    if ReadConfig.objects.get(pk="status").config_value == "on":
        Temperature.objects.create(
            timestamp=timezone.now(), value=received["payload"]["data"]["temperature"]
        )


async def capture_data() -> None:  # pragma: no cover
    """Read from the feed."""
    start = {"type": "start", "payload": {"query": "subscription { temperature }"}}
    async with websockets.connect(FEED_URI, subprotocols=["graphql-ws"]) as websocket:  # type: ignore
        await websocket.send(json.dumps(start))
        while True:
            data = await websocket.recv()
            received = json.loads(data)
            await sync_to_async(process_reading)(received)


class Command(BaseCommand):  # pragma: no cover
    """Custom command to consume the temperatures feed and store read values in db."""

    help = "Consume the temperatures feed and store read values in db"

    def handle(self, *args: tuple, **options: int) -> None:
        """Consume the feed in an infinite loop and persist data in db."""
        self.stdout.write(f"Launch consumption of temperature feed at {FEED_URI}")
        # setup initial reading status
        ReadConfig.objects.update_or_create(
            config_key="status", defaults={"config_value": "on"}
        )
        asyncio.run(capture_data())
