import logging

from pandas import DataFrame
from stockstats import StockDataFrame

from app.config import ALERTS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import df_from_database, SignalAlert


class BaseStrategy(BaseContainer):
    market = None
    at_time = None
    last_candle = None

    def run(self, market, at_time):
        self.at_time = at_time
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
        return self.wrap(df_from_database(self.market, self.at_time, limit))

    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
    def reshape_data(self, df, timedelta):
        logic = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
        return self.wrap(df.resample(timedelta).apply(logic))

    def wrap(self, df):
        return StockDataFrame.retype(df)

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
            self.at_time, self.strategy_name(), self.market, alert_type, message, self.last_candle['close']
        )
        self.lookup_object("redis_publisher").publish_data(ALERTS_CHANNEL, data)

    def candle(self, df: DataFrame, rewind=-1):
        return df.iloc[rewind].to_dict()

    def strategy_name(self):
        return self.__class__.__name__
