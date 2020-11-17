import pandas as pd

from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class MaCrossOverStrategy(BaseStrategy):
    CLOSE_BELOW_MA_SIGNAL = 'close-below-ma'
    CLOSE_ABOVE_MA_SIGNAL = 'close-above-ma'
    short_ma = 20
    long_ma = 50

    def calculate_indicators(self):
        df = self.load_df(limit=300)
        reshaped_df = self.reshape_data(df, timedelta='6H')
        _ = reshaped_df["close_{}_sma".format(self.short_ma)]
        _ = reshaped_df["close_{}_sma".format(self.long_ma)]
        return reshaped_df

    def can_sell(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle['close']
        calculated_short_ma = prev_candle["close_{}_sma".format(self.short_ma)]
        calculated_long_ma = prev_candle["close_{}_sma".format(self.long_ma)]
        return last_close < calculated_short_ma and last_close < calculated_long_ma

    def can_buy(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle['close']
        calculated_short_ma = prev_candle["close_{}_sma".format(self.short_ma)]
        calculated_long_ma = prev_candle["close_{}_sma".format(self.long_ma)]
        return last_close > calculated_short_ma and last_close > calculated_long_ma

    def alert_message(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle['close']
        calculated_short_ma = prev_candle["close_{}_sma".format(self.short_ma)]
        calculated_long_ma = prev_candle["close_{}_sma".format(self.long_ma)]
        return "Close {:.2f} - Short MA {:.2f} and Long MA {:.2f}".format(
            last_close,
            calculated_short_ma,
            calculated_long_ma,
        )
