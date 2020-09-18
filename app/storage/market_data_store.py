import threading
import logging
from app.common import b2s, json_from_bytes, uuid_gen
from app.models import CandleStick


class MarketDataStore(threading.Thread):
    pubsub = None

    def __init__(self, locator):
        super().__init__()
        self.locator = locator
        redis_instance = self.locator.s("redis")
        self.channels = ["binance-ohlcv-1m"]  # TODO: DRY
        self.pubsub = redis_instance.pubsub()
        self.pubsub.subscribe(self.channels)

    def run(self):
        for item in self.pubsub.listen():
            try:
                if self.can_handle(item):
                    event = json_from_bytes(item.get("data"))
                    event["id"] = uuid_gen()
                    CandleStick.insert(event).on_conflict_ignore().execute()
            except Exception as e:
                logging.error(e)

    def can_handle(self, item):
        return (
            item.get("type") == "message" and b2s(item.get("channel")) in self.channels
        )
