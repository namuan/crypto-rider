from datetime import timedelta

import mplfinance as mpf
import pandas as pd

from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class SimpleMovingAverageCrossTrendStrategy(BaseStrategy):

    def __init__(self, locator, params=dict()):
        BaseStrategy.__init__(self, locator)
        self.trend_ma = params.get("trend_ma") or 300
        self.trend_ma_indicator = "close_{}_sma".format(self.trend_ma)

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        reshaped_df = reshape_data(df, timedelta="1w")
        _ = reshaped_df[self.trend_ma_indicator]
        return reshaped_df

    def can_buy(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_trend_ma = prev_candle[self.trend_ma_indicator]
        return [last_close > calculated_trend_ma]

    def can_sell(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_trend_ma = prev_candle[self.trend_ma_indicator]
        return [last_close < calculated_trend_ma]

    def alert_message(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_trend_ma = prev_candle[self.trend_ma_indicator]
        return "Close {:.2f} - Trend SMA {:.2f}".format(
            last_close,
            calculated_trend_ma
        )

    def get_additional_plots(self, market, dt_since, dt_to):
        df = self.calculate_indicators()
        dt_end = dt_to - timedelta(days=1)
        return [
            mpf.make_addplot(
                df[self.trend_ma_indicator][dt_since:dt_end], linestyle="dashed"
            )
        ]
