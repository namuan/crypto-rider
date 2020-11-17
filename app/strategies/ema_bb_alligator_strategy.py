import pandas as pd
import ta
import logging
from app.common import crossed_above, crossed_below
from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class EMABBAlligatorStrategy(BaseStrategy):
    BUY_SIGNAL = 'buy_signal'
    SELL_SIGNAL = 'sell_signal'

    def apply(self):
        df = self.load_df(limit=300)
        reshaped_df = self.reshape_data(df, timedelta='H')

        ema = ta.trend.EMAIndicator(close=reshaped_df['close'], n=3)
        df['EMA_3'] = ema.ema_indicator()
        bb = ta.volatility.BollingerBands(close=reshaped_df['close'])
        df['BB_HBAND'] = bb.bollinger_hband()
        df['BB_HBAND_INDICATOR'] = bb.bollinger_hband_indicator()
        df['BB_LBAND'] = bb.bollinger_lband()
        df['BB_LBAND_INDICATOR'] = bb.bollinger_lband_indicator()
        df['BB_MAVG'] = bb.bollinger_mavg()
        df['BB_PBAND'] = bb.bollinger_pband()
        df['BB_BAND_WIDTH'] = bb.bollinger_wband()
        ao = ta.momentum.AwesomeOscillatorIndicator(high=reshaped_df['high'], low=reshaped_df['low'])
        df['AO'] = ao.ao()
        ema_xa_bb_mavg = crossed_above(df['EMA_3'], df['BB_MAVG'])
        ao_xo_zero = (df.shift(2)['AO'] < 0) & (df.shift(1)['AO'] > 0)
        vol_above_zero = df['volume'] > 0
        buy_signal = (ema_xa_bb_mavg) & (ao_xo_zero) & (vol_above_zero)
        logging.info(
            f"Buy Signal: {buy_signal.iloc[-1]} -> ema_xa_bb_mavg={ema_xa_bb_mavg.iloc[-1]}, ao_xo_zero={ao_xo_zero.iloc[-1]}, vol_above_zero={vol_above_zero.iloc[-1]}")

        ema_xb_bb_mavg = crossed_below(df['EMA_3'], df['BB_MAVG'])
        ao_xb_zero = (df.shift(2)['AO'] > 0) & (df.shift(-1)['AO'] < 0)
        sell_signal = (ema_xb_bb_mavg) & (ao_xb_zero) & (vol_above_zero)
        logging.info(
            f"Sell Signal: {sell_signal.iloc[-1]} -> ema_xa_bb_mavg={ema_xb_bb_mavg.iloc[-1]}, ao_xo_zero={ao_xb_zero.iloc[-1]}, vol_above_zero={vol_above_zero.iloc[-1]}")

        if bool(buy_signal[-1]) and self.is_new_alert_of_type(self.BUY_SIGNAL):
            self.build_and_send_alert(self.market, self.BUY_SIGNAL, df)
        elif bool(sell_signal[-1]) and self.is_new_alert_of_type(self.SELL_SIGNAL):
            self.build_and_send_alert(self.market, self.SELL_SIGNAL, df)

    def is_new_alert_of_type(self, alert_type):
        last_alert = self.find_last_alert_of(self.market)
        if not last_alert:
            return True

        return last_alert.alert_type != alert_type

    def build_and_send_alert(self, alert_market, alert_signal, df):
        last_close = self.prev_close(df)
        last_ao = df.iloc[-1]['AO']

        self.alert(
            "Market: **{}** - {}. Last Close: {}, Awesome Oscillator value: {}".format(
                alert_market,
                alert_signal,
                last_close,
                last_ao
            ),
            alert_signal
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
