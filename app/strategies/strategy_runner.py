import logging
import sched
from time import time

from app.config import (
    providers_fetch_delay,
    provider_markets,
)
from app.config.basecontainer import BaseContainer
from app.strategies.ema_bb_alligator_strategy import EMABBAlligatorStrategy
from app.strategies.ma_xo_strategy import MaCrossOverStrategy


class StrategyRunner(BaseContainer):
    scheduler = sched.scheduler()
    delay = providers_fetch_delay()
    markets = provider_markets()

    def __init__(self, locator):
        BaseContainer.__init__(self, locator)
        self.all_strategies = [
            # SimpleStrategy(locator),
            MaCrossOverStrategy(locator),
            EMABBAlligatorStrategy(locator),
        ]

    def start(self):
        logging.info("Running StrategyRunner every {} seconds".format(self.delay))
        self.scheduler.enter(self.delay, 1, self.run_strategies)
        self.scheduler.run()

    def run_strategies(self):
        for market in self.markets:
            for strategy in self.all_strategies:
                self.process_market_strategy(market, strategy)

        self.scheduler.enter(self.delay, 1, self.run_strategies)

    def process_market_strategy(self, market, strategy):
        alert_message, alert_type = strategy.run(market, int(time()) * 1000)
        if alert_message and alert_type:
            strategy.alert(alert_message, alert_type)
