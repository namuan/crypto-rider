import logging
from threading import Thread

from app.common import b2s, json_from_bytes, uuid_gen
from app.config.basecontainer import BaseContainer
from app.models import CandleStick


class MarketDataStore(Thread, BaseContainer):
    pubsub = None

    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator)
        redis_instance = self.lookup_service("redis")
        self.channels = ["binance-ohlcv-1m"]  # TODO: DRY
        self.pubsub = redis_instance.pubsub()
        self.pubsub.subscribe(self.channels)

    def run(self):
        for item in self.pubsub.listen():
            try:
                if self.can_handle(item):
                    event = json_from_bytes(item.get("data"))
                    CandleStick.save_from(event)
            except Exception as e:
                logging.error(e)

    def can_handle(self, item):
        return (
                item.get("type") == "message" and b2s(item.get("channel")) in self.channels
        )
