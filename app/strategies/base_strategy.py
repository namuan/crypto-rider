from threading import Thread
import logging

from pandas import DataFrame
from stockstats import StockDataFrame

from app.common import candle_event_name
from app.config import provider_exchange, provider_candle_timeframe, ALERTS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import df_from_database, SignalAlert


class BaseStrategy(Thread, BaseContainer):
    def __init__(self, locator):
        exchange_id = provider_exchange()
        timeframe = provider_candle_timeframe()
        Thread.__init__(self)
        BaseContainer.__init__(
            self,
            locator,
            subscription_channel=candle_event_name(exchange_id, timeframe),
        )
        self.last_event = None
        self.market = None

    def run(self) -> None:
        for event in self.pull_event():
            self.last_event = event
            df = self.calculate_indicators()
            if self.can_buy(df):
                message = self.alert_details(df)
                self.alert(message, "BUY")
            elif self.can_sell(df):
                message = self.alert_details(df)
                self.alert(message, "SELL")
            else:
                logging.info("Running {} -> No signal: {}".format(self.strategy_name(), self.candle(df)))


    def find_last_alert_of(self, market):
        return SignalAlert.select() \
            .where(SignalAlert.market == market) \
            .order_by(SignalAlert.timestamp.desc()) \
            .first()

    def load_df(self, limit=200):
        self.market = self.last_event.get("market")
        ts = self.last_event.get("timestamp")
        return self.wrap(df_from_database(self.market, ts, limit))

    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
    def reshape_data(self, df, timedelta):
        logic = {'open': 'first',
                 'high': 'max',
                 'low': 'min',
                 'close': 'last',
                 'volume': 'sum'}
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
            logging.info("{} - Found duplicate alert {} for market {}".format(
                self.strategy_name(),
                self.market,
                alert_type
            ))
            return

        data = SignalAlert.event(
            self.last_event.get("timestamp"), self.strategy_name(), self.market, alert_type, message
        )
        self.lookup_object("redis_publisher").publish_data(ALERTS_CHANNEL, data)

    def candle(self, df: DataFrame, rewind=0):
        return df.iloc[rewind].to_dict()

    def strategy_name(self):
        return self.__class__.__name__
