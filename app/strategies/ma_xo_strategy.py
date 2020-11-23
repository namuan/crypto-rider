import pandas as pd
import mplfinance as mpf
from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy
from datetime import timedelta

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class MaCrossOverStrategy(BaseStrategy):
    def __init__(self, locator, params=dict()):
        BaseStrategy.__init__(self, locator)
        self.short_ma = params.get("short_ma") or 20
        self.long_ma = params.get("long_ma") or 50
        self.short_ma_indicator = "close_{}_sma".format(self.short_ma)
        self.long_ma_indicator = "close_{}_sma".format(self.long_ma)

    def calculate_indicators(self):
        df = self.load_df(limit=1000)  # 6H * 300
        reshaped_df = reshape_data(df, timedelta="1d")
        _ = reshaped_df[self.short_ma_indicator]
        _ = reshaped_df[self.long_ma_indicator]
        return reshaped_df

    def can_buy(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_ma_indicator]
        calculated_long_ma = prev_candle[self.long_ma_indicator]
        return [last_close > calculated_short_ma, last_close > calculated_long_ma]

    def can_sell(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_ma_indicator]
        calculated_long_ma = prev_candle[self.long_ma_indicator]
        return [last_close < calculated_short_ma, last_close < calculated_long_ma]

    def alert_message(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_ma_indicator]
        calculated_long_ma = prev_candle[self.long_ma_indicator]
        return "Close {:.2f} - Short MA {:.2f} and Long MA {:.2f}".format(
            last_close,
            calculated_short_ma,
            calculated_long_ma,
        )

    def get_additional_plots(self, market, dt_since, dt_to):
        df = self.calculate_indicators()
        dt_end = dt_to - timedelta(days=1)
        return [
            mpf.make_addplot(
                df[self.short_ma_indicator][dt_since:dt_end], linestyle="dashed"
            ),
            mpf.make_addplot(
                df[self.long_ma_indicator][dt_since:dt_end], linestyle="dashed"
            ),
        ]
