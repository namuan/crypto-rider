from threading import Thread

from pandas import DataFrame

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

    def run(self) -> None:
        for event in self.pull_event():
            self.last_event = event
            self.apply()

    def load_df(self, limit=200):
        market = self.last_event.get("market")
        ts = self.last_event.get("timestamp")
        return df_from_database(market, ts, limit)

    def alert(self, message):
        data = SignalAlert.event(
            self.last_event.get("timestamp"), self.strategy_name(), message
        )
        self.lookup_object("redis_publisher").publish_data(ALERTS_CHANNEL, data)

    def candle(self, df: DataFrame, rewind=0):
        return df.iloc[rewind].to_dict()

    def strategy_name(self):
        return self.__class__.__name__
