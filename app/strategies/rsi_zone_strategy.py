from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy
from datetime import timedelta
import mplfinance as mpf


class RsiZoneStrategy(BaseStrategy):
    def __init__(self, locator, params=dict()):
        BaseStrategy.__init__(self, locator)
        self.rsi = params.get("rsi") or 4
        self.rsi_indicator = "rsi_{}".format(self.rsi)
        self.rsi_buy_limit = params.get("rsi_buy_limit") or 25
        self.rsi_sell_limit = params.get("rsi_sell_limit") or 55
        self.trend_indicator = params.get("trend_indicator") or "close_200_sma"

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        reshaped_df = reshape_data(df, timedelta="1d")
        _ = reshaped_df[self.rsi_indicator]
        _ = reshaped_df[self.trend_indicator]
        return reshaped_df

    def can_buy(self, df):
        candle = self.candle(df)
        return [
            candle["close"] > candle[self.trend_indicator],
            candle[self.rsi_indicator] < self.rsi_buy_limit,
        ]

    def can_sell(self, df):
        candle = self.candle(df)
        return [
            candle["close"] > candle[self.trend_indicator],
            candle[self.rsi_indicator] > self.rsi_sell_limit,
        ]

    def alert_message(self, df):
        candle = self.candle(df)
        return "Close {}, RSI({}) {}, Trend {}".format(
            candle["close"],
            self.rsi,
            candle[self.rsi_indicator],
            candle[self.trend_indicator],
        )
