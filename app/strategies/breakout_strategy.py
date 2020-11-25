from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy


class BreakoutStrategy(BaseStrategy):
    def __init__(self, locator, params=dict()):
        BaseStrategy.__init__(self, locator)
        self.max_range = params.get("max_range") or 10
        self.ma_range = params.get("max_range") or 50
        self.higher_high = "close_{}_max".format(self.max_range)
        self.ma_indicator = "close_{}_sma".format(self.ma_range)
        self.trend_indicator = params.get("trend_indicator") or "close_200_sma"
        self.timeframe = params.get("timeframe") or "1h"

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        reshaped_df = reshape_data(df, timedelta=self.timeframe)
        reshaped_df[self.higher_high] = (
            reshaped_df["close"].shift().rolling(self.max_range).max()
        )
        _ = reshaped_df[self.ma_indicator]
        _ = reshaped_df[self.trend_indicator]
        return reshaped_df

    def can_buy(self, df):
        candle = self.candle(df)
        last_close = candle["close"]
        return [
            last_close > candle[self.trend_indicator],
            last_close > candle[self.higher_high],
        ]

    def can_sell(self, df):
        candle = self.candle(df)
        last_close = candle["close"]
        return [
            candle["close"] > candle[self.trend_indicator],
            last_close < candle[self.ma_indicator],
        ]

    def alert_message(self, df):
        candle = self.candle(df)
        return "Close {}, Previous Max({}) => {}, MA({}) => {}".format(
            candle["close"],
            self.max_range,
            candle[self.higher_high],
            self.ma_range,
            candle[self.ma_indicator],
        )
