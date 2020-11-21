import logging
import sched
from datetime import datetime
from time import time

import pandas as pd

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

    def process_market_strategy(self, market, strategy, start=int(time())):
        alert_message, alert_type = strategy.run(market, start * 1000)
        if alert_message and alert_type:
            strategy.alert(alert_message, alert_type)

    def run_back_test(self, market, since, to, selected_strategy):
        self.lookup_object("alert_data_store").clear_data()

        dt_since = datetime.strptime(since, "%Y-%m-%d")
        dt_to = datetime.strptime(to, "%Y-%m-%d")
        logging.info("Running backtest for {}, from {} to {} with {}".format(
            market,
            dt_since,
            dt_to,
            selected_strategy
        ))

        for strategy in self.all_strategies:
            if type(strategy).__name__ == selected_strategy:
                bt_range = pd.date_range(start=since, end=to)
                for r in bt_range:
                    logging.info("~~ On {}".format(r))
                    self.process_market_strategy(market, strategy, start=r.timestamp())
