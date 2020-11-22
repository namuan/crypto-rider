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
from app.strategies.close_x_ema_strategy import CloseCrossEmaStrategy
from app.strategies.ema_bb_alligator_strategy import EMABBAlligatorStrategy
from app.strategies.ma_xo_strategy import MaCrossOverStrategy
from app.strategies.rsi_zone_strategy import RsiZoneStrategy
from app.strategies.simple_strategy import SimpleStrategy


class StrategyRunner(BaseContainer):
    scheduler = sched.scheduler()
    delay = providers_fetch_delay()
    markets = provider_markets()

    def __init__(self, locator):
        BaseContainer.__init__(self, locator)
        self.all_strategies = [
            SimpleStrategy(locator),
            RsiZoneStrategy(locator),
            CloseCrossEmaStrategy(locator),
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

    def run_back_test(self, market, str_since, str_to, provided_strategy):
        selected_strategy = next(
            (s for s in self.all_strategies if type(s).__name__ == provided_strategy),
            None,
        )
        if not selected_strategy:
            logging.warning("Unable to find strategy {}".format(provided_strategy))
            return

        self.lookup_object("alert_data_store").clear_data()
        self.lookup_object("order_data_store").clear_data()

        dt_since = datetime.strptime(str_since, "%Y-%m-%d")
        dt_to = datetime.strptime(str_to, "%Y-%m-%d")
        logging.info(
            "Running backtest for {}, from {} to {} with {}".format(
                market, dt_since, dt_to, provided_strategy
            )
        )

        bt_range = pd.date_range(start=str_since, end=str_to)
        for dt_in_range in bt_range:
            logging.info("~~ On {}".format(dt_in_range))
            self.process_market_strategy(
                market, selected_strategy, ts_start=dt_in_range.timestamp()
            )

        self.lookup_object("order_data_store").force_close(market, dt_since, dt_to)
        self.lookup_object("report_publisher").generate_report(market, dt_since, dt_to)

        # Plot chart
        additional_plots = selected_strategy.get_additional_plots(
            market, dt_since, dt_to
        )
        self.lookup_object("report_publisher").plot_chart(
            market, dt_since, dt_to, additional_plots
        )

    def process_market_strategy(self, market, strategy, ts_start=int(time())):
        alert_message, alert_type = strategy.run(market, ts_start * 1000)
        if alert_message and alert_type:
            strategy.alert(alert_message, alert_type)
