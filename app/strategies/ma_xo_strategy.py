import pandas as pd

from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class MaCrossOverStrategy(BaseStrategy):
    CLOSE_BELOW_MA_SIGNAL = 'close-below-ma'
    CLOSE_ABOVE_MA_SIGNAL = 'close-above-ma'
    CLOSE_BETWEEN_MA_SIGNAL = 'close-between-ma'
    short_ma = 20
    long_ma = 100
    last_alert = {}

    def apply(self):
        df = self.load_df(limit=300)
        reshaped_df = self.reshape_data(df, timedelta='6H')

        calculated_short_ma = self.calc_ma(reshaped_df, self.short_ma)
        calculated_long_ma = self.calc_ma(reshaped_df, self.long_ma)
        last_close = self.close(reshaped_df)

        close_below_ma = self.calculate_close_below_ma(last_close, calculated_short_ma, calculated_long_ma)
        close_above_ma = self.calculate_close_above_ma(last_close, calculated_short_ma, calculated_long_ma)

        if close_below_ma and self.is_new_alert_of_type(self.CLOSE_BELOW_MA_SIGNAL):
            self.build_and_send_alert(self.market, self.CLOSE_BELOW_MA_SIGNAL, self.close(df), calculated_short_ma,
                                      calculated_long_ma)
        elif close_above_ma and self.is_new_alert_of_type(self.CLOSE_ABOVE_MA_SIGNAL):
            self.build_and_send_alert(self.market, self.CLOSE_ABOVE_MA_SIGNAL, self.close(df), calculated_short_ma,
                                      calculated_long_ma)
        elif self.is_new_alert_of_type(self.CLOSE_BETWEEN_MA_SIGNAL):
            self.build_and_send_alert(self.market, self.CLOSE_BETWEEN_MA_SIGNAL, self.close(df), calculated_short_ma,
                                      calculated_long_ma)

    def is_new_alert_of_type(self, alert_type):
        if not self.last_alert.get(self.market, False):
            return True

        return self.last_alert.get(self.market) != alert_type

    def build_and_send_alert(self, alert_market, alert_signal, last_close, calculated_short_ma, calculated_long_ma):
        self.last_alert[alert_market] = alert_signal
        self.alert(
            "Market: **{}** - Close {} {} Short MA {} and Long MA {}".format(
                alert_market,
                last_close,
                alert_signal,
                calculated_short_ma,
                calculated_long_ma,
            )
        )

    def calc_ma(self, df, ma):
        return df["close_{}_sma".format(ma)].iloc[-1]

    def calculate_close_below_ma(self, last_close, calculated_short_ma, calculated_long_ma):
        return last_close < calculated_short_ma and last_close < calculated_long_ma

    def calculate_close_above_ma(self, last_close, calculated_short_ma, calculated_long_ma):
        return last_close > calculated_short_ma and last_close > calculated_long_ma

    def close(self, df):
        return self.candle(df)["close"]

    def prev_close(self, df):
        return self.candle(df, rewind=1)["close"]
