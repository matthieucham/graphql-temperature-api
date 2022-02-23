import json
import websockets
import asyncio
from typing import Any, Dict, List
from django.utils import timezone
from asgiref.sync import sync_to_async

from backend.settings import FEED_URI
from api.models import Temperature


class FeedConsumer:

    # Flag controlling the consuming loop
    _is_consuming = False

    async def _capture_data(self) -> None:  # pragma: no cover
        """Read from the feed."""
        start = {"type": "start", "payload": {"query": "subscription { temperature }"}}
        async with websockets.connect(FEED_URI, subprotocols=["graphql-ws"]) as websocket:  # type: ignore
            await websocket.send(json.dumps(start))
            while self._is_consuming:
                data = await websocket.recv()
                received = json.loads(data)
                await sync_to_async(self._process_reading)(received)

    def _process_reading(self, received: Dict[str, Any]) -> None:
        """Persist an incoming temperature reading.

        Args:
            received (Dict[str,Any]): received reading (json)

        """
        Temperature.objects.create(
            timestamp=timezone.now(), value=received["payload"]["data"]["temperature"]
        )

    def start(self):
        """Consume the feed in an infinite loop and persist data by batches."""
        if not self._is_consuming:
            self._is_consuming = True
            asyncio.run(self._capture_data())

    def stop(self):
        """End the consuming loop."""
        self._is_consuming = False
        asyncio.run(self._capture_data())
