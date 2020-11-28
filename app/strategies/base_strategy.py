import logging

from pandas import DataFrame
from time import time

from app.config.basecontainer import BaseContainer
from app.models import SignalAlert


class Position:
    def __init__(self, open_dt, open_candle, close_dt=None, close_candle=None):
        self.open_dt = open_dt
        self.close_dt = close_dt
        self.open_candle = open_candle
        self.close_candle = close_candle

    def is_open(self):
        return self.open_dt and not self.close_dt


class BaseStrategy(BaseContainer):
    market = None
    ts_at_run = None
    last_candle = None
    current_position = None

    def run(self, market, ts_at_run):
        self.ts_at_run = ts_at_run or int(time() * 1000)
        self.market = market
        alert_message, alert_type = None, None
        df = self.calculate_indicators()
        self.last_candle = self.candle(df)

        if not self._has_open_position() and self.evaluate_conditions(self.can_buy(df)):
            message = self.alert_message(df)
            alert_message, alert_type = message, "BUY"
            self._open_position(df)
        elif self._has_open_position() and self.evaluate_conditions(self.can_sell(df)):
            message = self.alert_message(df)
            alert_message, alert_type = message, "SELL"
            self._close_position(df)
        else:
            logging.info(
                "Running {} -> No signal: {}".format(
                    self.strategy_name(), self.candle(df)
                )
            )

        return alert_message, alert_type

    def _has_open_position(self):
        return self.current_position and self.current_position.is_open()

    def _open_position(self, df):
        self.current_position = Position(
            open_dt=df.index[-1], open_candle=self.candle(df)
        )

    def _close_position(self, df):
        if self.current_position:
            self.current_position.close_dt = df.index[-1]
            self.current_position.close_candle = self.candle(df)

    def position(self):
        return self.current_position

    def find_last_alert_of(self, market, strategy):
        return (
            SignalAlert.select()
            .where(SignalAlert.market == market, SignalAlert.strategy == strategy)
            .order_by(SignalAlert.timestamp.desc())
            .first()
        )

    def load_df(self, limit=200):
        return self.lookup_object("market_data_store").fetch_data_from(
            self.market, self.ts_at_run, limit
        )

    def is_new_alert_of_type(self, alert_type):
        last_alert = self.find_last_alert_of(self.market, self.strategy_name())
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

        self.lookup_object("alert_data_store").save_alert(data)
        self.lookup_object("broker").execute_trade(data)

    def candle(self, df: DataFrame, rewind=-1):
        return df.iloc[rewind].to_dict()

    def strategy_name(self):
        return self.__class__.__name__

    def get_additional_plots(self, market, dt_since, dt_to):
        return []

    def evaluate_conditions(self, conditions):
        return all(conditions)
