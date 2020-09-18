import logging
import sched

import ccxt

from app.config import providers_fetch_delay
from app.config.basecontainer import BaseContainer
from app.models import CandleStick


class MarketDataProvider(BaseContainer):
    scheduler = sched.scheduler()
    delay = providers_fetch_delay()
    exchange = "binance"
    binance = ccxt.binance()
    market = "BTC/USDT"  # TODO: Move to config
    timeframe = "1m"  # TODO: Move to config

    def start(self):
        logging.info("Running MarketDataProvider every {} seconds".format(self.delay))
        self.scheduler.enter(self.delay, 1, self.provide_market_data)
        self.scheduler.run()

    def provide_market_data(self):
        candle_data = self.binance.fetch_ohlcv(self.market, self.timeframe, limit=1)[0]
        data = CandleStick.event(self.exchange, self.market, *candle_data)
        self.lookup_object("redis_publisher").publish_data(
            self.exchange, "ohlcv-{}".format(self.timeframe), data
        )
        self.scheduler.enter(self.delay, 1, self.provide_market_data)
