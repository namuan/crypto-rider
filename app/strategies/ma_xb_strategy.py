import pandas as pd

from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class MaCrossBelowStrategy(BaseStrategy):
    short_ma: int = 20
    long_ma: int = 100

    def apply(self):
        df = self.load_df(limit=300)
        reshaped_df = self.reshape_data(df, timedelta='6H')
        signal = self.calculate_signal(reshaped_df)
        if signal:
            self.alert(
                "Close cross below Short MA {} and Long MA {} - Current: {}".format(
                    self.short_ma, self.long_ma, self.close(df)
                )
            )

    def calculate_signal(self, df):
        return (
                (df['close'] < df[f"close_{self.short_ma}_sma"]) &
                (df['close'] < df[f"close_{self.long_ma}_sma"])
        ).iloc[-1]

    def close(self, df):
        return self.candle(df)["close"]

    def prev_close(self, df):
        return self.candle(df, rewind=1)["close"]
