import pandas as pd

from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class MaCrossOverStrategy(BaseStrategy):
    CLOSE_BELOW_MA_SIGNAL = "close-below-ma"
    CLOSE_ABOVE_MA_SIGNAL = "close-above-ma"
    short_ma = 20
    long_ma = 50
    short_ma_indicator = "close_{}_sma".format(short_ma)
    long_ma_indicator = "close_{}_sma".format(long_ma)

    def calculate_indicators(self):
        df = self.load_df(limit=1000)  # 6H * 300
        reshaped_df = reshape_data(df, timedelta="1d")
        _ = reshaped_df[self.short_ma_indicator]
        _ = reshaped_df[self.long_ma_indicator]
        return reshaped_df

    def can_sell(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_ma_indicator]
        calculated_long_ma = prev_candle[self.long_ma_indicator]
        return last_close < calculated_short_ma and last_close < calculated_long_ma

    def can_buy(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_ma_indicator]
        calculated_long_ma = prev_candle[self.long_ma_indicator]
        return last_close > calculated_short_ma and last_close > calculated_long_ma

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
