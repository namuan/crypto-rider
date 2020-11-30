from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy


class CloseCrossEmaStrategy(BaseStrategy):
    short_ema = 20
    short_indicator = "close_{}_ema".format(short_ema)
    long_ema = 50
    long_indicator = "close_{}_ema".format(long_ema)

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        _ = df[self.short_indicator]
        _ = df[self.long_indicator]
        return df

    def can_sell(self, df):
        prev_candle = self.candle(df)
        candle_2_close = self.candle(df, rewind=-2)["close"]
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_indicator]
        calculated_long_ma = prev_candle[self.long_indicator]
        return [
            candle_2_close < calculated_short_ma
            and candle_2_close < calculated_long_ma,
            last_close < calculated_short_ma and last_close < calculated_long_ma,
            calculated_short_ma < calculated_long_ma,
        ]

    def can_buy(self, df):
        prev_candle = self.candle(df)
        candle_2_close = self.candle(df, rewind=-2)["close"]
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_indicator]
        calculated_long_ma = prev_candle[self.long_indicator]
        return [
            candle_2_close > calculated_short_ma
            and candle_2_close > calculated_long_ma,
            last_close > calculated_short_ma and last_close > calculated_long_ma,
            calculated_short_ma > calculated_long_ma,
        ]

    def alert_message(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_indicator]
        calculated_long_ma = prev_candle[self.long_indicator]
        return "Close {:.2f} - Short MA {:.2f} and Long MA {:.2f}".format(
            last_close,
            calculated_short_ma,
            calculated_long_ma,
        )
