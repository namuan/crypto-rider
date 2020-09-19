import logging
from threading import Thread

from pandas import DataFrame

from app.common import candle_event_name, json_from_bytes, b2s
from app.config import provider_exchange, provider_candle_timeframe
from app.config.basecontainer import BaseContainer
from app.models import df_from_database


class BaseStrategy(Thread, BaseContainer):
    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator)
        redis_instance = self.lookup_service("redis")
        exchange_id = provider_exchange()
        timeframe = provider_candle_timeframe()
        self.channels = [candle_event_name(exchange_id, timeframe)]
        self.pubsub = redis_instance.pubsub()
        self.pubsub.subscribe(self.channels)
        self.last_event = None

    def run(self) -> None:
        for item in self.pubsub.listen():
            try:
                if self._can_handle(item):
                    self.last_event = json_from_bytes(item.get("data"))
                    self.apply()
            except Exception as e:
                logging.error(e)

    def load_df(self, limit=200):
        market = self.last_event.get('market')
        ts = self.last_event.get('timestamp')
        return df_from_database(market, ts, limit)

    def alert(self, signal):
        logging.info("Send alert signal: {}".format(signal))

    def _can_handle(self, item):
        return (
                item.get("type") == "message" and b2s(item.get("channel")) in self.channels
        )

    def candle(self, df: DataFrame, rewind=0):
        return df.iloc[rewind].to_dict()
