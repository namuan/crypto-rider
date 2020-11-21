import logging

from pandas import DataFrame

from app.config import ALERTS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import market_data, SignalAlert


class BaseStrategy(BaseContainer):
    market = None
    ts_at_run = None
    last_candle = None

    def run(self, market, ts_at_run):
        self.ts_at_run = ts_at_run
        self.market = market
        alert_message, alert_type = None, None
        df = self.calculate_indicators()
        if self.can_buy(df):
            message = self.alert_message(df)
            alert_message, alert_type = message, "BUY"
        elif self.can_sell(df):
            message = self.alert_message(df)
            alert_message, alert_type = message, "SELL"
        else:
            logging.info(
                "Running {} -> No signal: {}".format(
                    self.strategy_name(), self.candle(df)
                )
            )

        self.last_candle = self.candle(df)
        return alert_message, alert_type

    def find_last_alert_of(self, market):
        return (
            SignalAlert.select()
                .where(SignalAlert.market == market)
                .order_by(SignalAlert.timestamp.desc())
                .first()
        )

    def load_df(self, limit=200):
        return market_data(self.market, self.ts_at_run, limit)

    def is_new_alert_of_type(self, alert_type):
        last_alert = self.find_last_alert_of(self.market)
        if not last_alert:
            return True

        return last_alert.alert_type != alert_type

    def alert(self, message, alert_type):
        if not self.is_new_alert_of_type(alert_type):
            logging.info(
                "{} - Found duplicate alert {} for market {}".format(
                    self.strategy_name(), self.market, alert_type
                )
            )
            return

        data = SignalAlert.event(
            self.ts_at_run,
            self.strategy_name(),
            self.market,
            alert_type,
            message,
            self.last_candle["close"],
        )

        self.lookup_object("redis_publisher").publish_data(ALERTS_CHANNEL, data)

    def candle(self, df: DataFrame, rewind=-1):
        return df.iloc[rewind].to_dict()

    def strategy_name(self):
        return self.__class__.__name__
