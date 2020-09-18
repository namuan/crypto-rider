import logging
from threading import Thread

from app.common import b2s, json_from_bytes, candle_event_name
from app.config import provider_exchange, provider_candle_timeframe
from app.config.basecontainer import BaseContainer
from app.models import CandleStick


class MarketDataStore(Thread, BaseContainer):
    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator)
        redis_instance = self.lookup_service("redis")
        exchange_id = provider_exchange()
        timeframe = provider_candle_timeframe()
        self.channels = [candle_event_name(exchange_id, timeframe)]
        self.pubsub = redis_instance.pubsub()
        self.pubsub.subscribe(self.channels)

    def run(self):
        for item in self.pubsub.listen():
            try:
                if self._can_handle(item):
                    event = json_from_bytes(item.get("data"))
                    CandleStick.save_from(event)
            except Exception as e:
                logging.error(e)

    def _can_handle(self, item):
        return (
                item.get("type") == "message" and b2s(item.get("channel")) in self.channels
        )
