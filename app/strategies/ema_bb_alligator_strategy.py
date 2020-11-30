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
        _ = df["close_3_ema"]
        _ = df["boll"]
        ao = ta.momentum.AwesomeOscillatorIndicator(high=df["high"], low=df["low"])
        df["AO"] = ao.ao()
        return df

    def can_sell(self, df):
        prev_candle = self.candle(df)
        last_ema = prev_candle["close_3_ema"]
        last_bb = prev_candle["boll"]
        return [
            last_ema < last_bb,
            (self.candle(df, rewind=-2)["AO"] > 0)
            & (self.candle(df, rewind=-1)["AO"] < 0),
            prev_candle["volume"] > 0,
        ]

    def can_buy(self, df):
        prev_candle = self.candle(df)
        last_ema = prev_candle["close_3_ema"]
        last_bb = prev_candle["boll"]
        return [
            last_ema > last_bb,
            (self.candle(df, rewind=-2)["AO"] < 0)
            & (self.candle(df, rewind=-1)["AO"] > 0),
            prev_candle["volume"] > 0,
        ]

    def alert_message(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle["close"]
        last_ao = prev_candle["AO"]
        return (
            "Close: {:.2f}, Awesome Oscillator value: {:.2f}".format(
                last_close, last_ao
            ),
        )
