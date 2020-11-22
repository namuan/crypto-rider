import logging
from datetime import datetime
from threading import Thread

import pandas as pd

from app.common import b2s, json_from_bytes, candle_event_name, wrap
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

    def fetch_data_between(self, market, dt_from, dt_to):
        ts_from = dt_from.timestamp() * 1000
        ts_to = dt_to.timestamp() * 1000

        logging.info(
            "Getting entries for market {} from database from {} => {}".format(
                market, ts_from, ts_to
            )
        )
        query = CandleStick.select().where(
            CandleStick.market == market,
            CandleStick.timestamp >= ts_from,
            CandleStick.timestamp <= ts_to,
        )
        df = pd.DataFrame(list(query.dicts()))
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
        return wrap(df)

    def fetch_data_from(self, market, ts, limit):
        logging.info(
            "Getting last {} entries for market {} from database from {} => {}".format(
                limit, market, ts, datetime.fromtimestamp(ts / 1000)
            )
        )
        query = (
            CandleStick.select()
            .where(CandleStick.market == market, CandleStick.timestamp <= ts)
            .order_by(CandleStick.timestamp.desc())
            .limit(limit)
        )
        df = pd.DataFrame(list(query.dicts()))
        df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
        return wrap(df)

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
