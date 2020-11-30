from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy


class SimpleStrategy(BaseStrategy):
    def __init__(self, locator, params=dict()):
        BaseStrategy.__init__(self, locator)
        self.trend_ma = params.get("trend_ma") or 300
        self.trend_ma_indicator = "close_{}_sma".format(self.trend_ma)

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        return df

    def can_sell(self, df):
        candle = self.candle(df)
        prev_candle = self.candle(df, rewind=-2)
        return [prev_candle["close"] > candle["close"]]

    def can_buy(self, df):
        candle = self.candle(df)
        prev_candle = self.candle(df, rewind=-2)
        return [candle["close"] > prev_candle["close"]]

    def alert_message(self, df):
        candle = self.candle(df)
        prev_candle = self.candle(df, rewind=-2)
        return "Close(Prev {}, Current {})".format(
            prev_candle["close"], candle["close"]
        )
