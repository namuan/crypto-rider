import json
import logging
import sched
from datetime import datetime
import ccxt

from app.common import candle_event_name
from app.config import (
    providers_fetch_delay,
    provider_markets,
    provider_exchange,
    provider_candle_timeframe,
)
from app.config.basecontainer import BaseContainer
from app.models import CandleStick


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
        logging.info("Finished loading historical market data. Total {}".format(len(candle_data_items)))

    def download_historical_data(self, market, since):
        ts = datetime.strptime(since, "%Y-%m-%d")
        logging.info("Downloading historical data for {} from exchange {} since {}".format(
            market,
            self.exchange_id,
            ts
        ))
        candle_data_items = self.exchange.fetch_ohlcv(market, '1d', since=ts.timestamp() * 1000)
        for candle_data in candle_data_items:
            data = CandleStick.event(self.exchange_id, market, *candle_data)
            self.lookup_object("redis_publisher").publish_data(
                candle_event_name(self.exchange_id, self.timeframe), data
            )
        logging.info("Finished loading historical market data. Total {}".format(len(candle_data_items)))