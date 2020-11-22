from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy


class CloseCrossEmaStrategy(BaseStrategy):
    short_ema = 20
    short_indicator = "close_{}_ema".format(short_ema)
    long_ema = 50
    long_indicator = "close_{}_ema".format(long_ema)

    def calculate_indicators(self):
        df = self.load_df(limit=1000)  # 6H * 300
        reshaped_df = reshape_data(df, timedelta="1d")
        _ = reshaped_df[self.short_indicator]
        _ = reshaped_df[self.long_indicator]
        return reshaped_df

    def can_sell(self, df):
        prev_candle = self.candle(df)
        candle_2_close = self.candle(df, rewind=-2)['close']
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_indicator]
        calculated_long_ma = prev_candle[self.long_indicator]
        cond_1 = candle_2_close < calculated_short_ma and candle_2_close < calculated_long_ma
        cond_2 = last_close < calculated_short_ma and last_close < calculated_long_ma
        cond_3 = calculated_short_ma < calculated_long_ma
        return cond_1 and cond_2 and cond_3

    def can_buy(self, df):
        prev_candle = self.candle(df)
        candle_2_close = self.candle(df, rewind=-2)['close']
        last_close = prev_candle["close"]
        calculated_short_ma = prev_candle[self.short_indicator]
        calculated_long_ma = prev_candle[self.long_indicator]
        cond_1 = candle_2_close > calculated_short_ma and candle_2_close > calculated_long_ma
        cond_2 = last_close > calculated_short_ma and last_close > calculated_long_ma
        cond_3 = calculated_short_ma > calculated_long_ma
        return cond_1 and cond_2 and cond_3

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

    def get_additional_plots(self, market, dt_since, dt_to):
        return []
