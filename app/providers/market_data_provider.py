import logging
import sched

import ccxt

from app.config import providers_fetch_delay, provider_markets, provider_exchange
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
    timeframe = "1m"  # TODO: Move to config

    def start(self):
        logging.info("Running MarketDataProvider every {} seconds".format(self.delay))
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
                self.exchange_id, "ohlcv-{}".format(self.timeframe), data
            )
        self.scheduler.enter(self.delay, 1, self.provide_market_data)
