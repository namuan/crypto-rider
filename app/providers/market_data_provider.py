import sched

import ccxt

from app.config import providers_fetch_delay


class MarketDataProvider:
    scheduler = sched.scheduler()
    delay = providers_fetch_delay()
    exchange = "binance"
    binance = ccxt.binance()
    symbol = "BTC/USDT"  # TODO: Move to config
    timeframe = "1m"  # TODO: Move to config

    def __init__(self, locator):
        self.locator = locator

    def start(self):
        print("Starting scheduler for {}".format(self.delay))
        self.scheduler.enter(self.delay, 1, self.provide_market_data)
        self.scheduler.run()

    def provide_market_data(self):
        print("Provide Market Data")
        ts, op, hi, lo, cl, vol = self.binance.fetch_ohlcv(
            self.symbol, self.timeframe, limit=1
        )[0]
        data = dict(
            exchange=self.exchange,
            symbol=self.symbol,
            timestamp=ts,
            open=op,
            high=hi,
            low=lo,
            close=cl,
            volume=vol,
        )
        self.locator.o("redis_publisher").publish_data(
            self.exchange, "ohlcv-{}".format(self.timeframe), data
        )
        self.scheduler.enter(self.delay, 1, self.provide_market_data)