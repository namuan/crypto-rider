import json
import logging
import sched
from datetime import datetime
import ccxt
from time import sleep

from app.common import candle_event_name
from app.config import (
    providers_fetch_delay,
    provider_markets,
    provider_exchange,
    provider_candle_timeframe,
)
from app.config.basecontainer import BaseContainer
from app.models import CandleStick
import pandas as pd


def exchange_factory(exchange_id):
    exchange_clazz = getattr(ccxt, exchange_id)
    return exchange_clazz()


class MarketDataProvider(BaseContainer):
    scheduler = sched.scheduler()
    delay = providers_fetch_delay()
    exchange_id = provider_exchange()
    exchange = exchange_factory(exchange_id)
    markets = provider_markets()
    timeframe = provider_candle_timeframe()

    def start(self, skip_wait):
        if skip_wait:
            logging.info("Running MarketDataProvider once")
            self.provide_market_data()
        else:
            logging.info(
                "Running MarketDataProvider every {} seconds".format(self.delay)
            )
            self.scheduler.enter(self.delay, 1, self.provide_market_data)
            self.scheduler.run()

    def provide_market_data(self):
        for market in self.markets:
            logging.info(
                "Fetching data for {} in time frame {}".format(market, self.timeframe)
            )
            candle_data = self.exchange.fetch_ohlcv(market, self.timeframe, limit=1)[0]
            data = CandleStick.event(self.exchange_id, market, *candle_data)
            self.lookup_object("redis_publisher").publish_data(
                candle_event_name(self.exchange_id, self.timeframe), data
            )
        self.scheduler.enter(self.delay, 1, self.provide_market_data)

    def load_historical_data(self, market, data_file):
        logging.info("Loading historical data for {}".format(market))
        candle_data_items = json.loads(data_file.read())
        for candle_data in candle_data_items:
            data = CandleStick.event(self.exchange_id, market, *candle_data)
            self.lookup_object("redis_publisher").publish_data(
                candle_event_name(self.exchange_id, self.timeframe), data
            )
        logging.info(
            "Finished loading historical market data. Total {}".format(
                len(candle_data_items)
            )
        )

    def download_historical_data(self, market, str_since):
        dt_since = datetime.strptime(str_since, "%Y-%m-%d")
        dt_to = datetime.now()
        str_to = dt_to.strftime("%Y-%m-%d")

        logging.info(
            "Downloading historical data for {} from exchange {} from {} to {}".format(
                market, self.exchange_id, dt_since, dt_to
            )
        )

        bt_range = pd.date_range(start=str_since, end=str_to)
        for dt_in_range in bt_range:
            candle_data_items = self.exchange.fetch_ohlcv(
                market, "1h", since=dt_in_range.timestamp() * 1000, limit=24
            )
            for candle_data in candle_data_items:
                data = CandleStick.event(self.exchange_id, market, *candle_data)
                self.lookup_object("redis_publisher").publish_data(
                    candle_event_name(self.exchange_id, self.timeframe), data
                )
            logging.info(
                "Finished loading historical market data. Total {}".format(
                    len(candle_data_items)
                )
            )
            sleep(0.5)
