import pandas as pd
import ta

from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class EMABBAlligatorStrategy(BaseStrategy):
    BUY_SIGNAL = "buy_signal"
    SELL_SIGNAL = "sell_signal"

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        reshaped_df = reshape_data(df, timedelta="1d")
        _ = reshaped_df['close_3_ema']
        _ = reshaped_df['boll']
        ao = ta.momentum.AwesomeOscillatorIndicator(
            high=reshaped_df["high"], low=reshaped_df["low"]
        )
        reshaped_df["AO"] = ao.ao()
        return reshaped_df

    def can_sell(self, df):
        prev_candle = self.candle(df)
        last_ema = prev_candle["close_3_ema"]
        last_bb = prev_candle["boll"]
        ema_xb_bb_mavg = last_ema < last_bb
        ao_xb_zero = (self.candle(df, rewind=-2)["AO"] > 0) & (self.candle(df, rewind=-1)["AO"] < 0)
        vol_above_zero = prev_candle["volume"] > 0
        result = ema_xb_bb_mavg and ao_xb_zero and vol_above_zero
        return result

    def can_buy(self, df):
        prev_candle = self.candle(df)
        last_ema = prev_candle["close_3_ema"]
        last_bb = prev_candle["boll"]
        ema_xa_bb_mavg = last_ema > last_bb
        ao_xo_zero = (self.candle(df, rewind=-2)["AO"] < 0) & (self.candle(df, rewind=-1)["AO"] > 0)
        vol_above_zero = prev_candle["volume"] > 0
        result = ema_xa_bb_mavg and ao_xo_zero and vol_above_zero
        return result

    def alert_message(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        last_ao = prev_candle["AO"]
        return (
            "Close: {:.2f}, Awesome Oscillator value: {:.2f}".format(
                last_close, last_ao
            ),
        )
