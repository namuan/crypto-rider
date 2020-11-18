import pandas as pd
import ta

from app.common import crossed_above, crossed_below
from app.strategies.base_strategy import BaseStrategy

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)


class EMABBAlligatorStrategy(BaseStrategy):
    BUY_SIGNAL = 'buy_signal'
    SELL_SIGNAL = 'sell_signal'

    def calculate_indicators(self):
        df = self.load_df(limit=50 * 60) # 1H * 300
        reshaped_df = self.reshape_data(df, timedelta='H')
        ema = ta.trend.EMAIndicator(close=reshaped_df['close'], n=3)
        reshaped_df['EMA_3'] = ema.ema_indicator()
        bb = ta.volatility.BollingerBands(close=reshaped_df['close'])
        reshaped_df['BB_HBAND'] = bb.bollinger_hband()
        reshaped_df['BB_HBAND_INDICATOR'] = bb.bollinger_hband_indicator()
        reshaped_df['BB_LBAND'] = bb.bollinger_lband()
        reshaped_df['BB_LBAND_INDICATOR'] = bb.bollinger_lband_indicator()
        reshaped_df['BB_MAVG'] = bb.bollinger_mavg()
        reshaped_df['BB_PBAND'] = bb.bollinger_pband()
        reshaped_df['BB_BAND_WIDTH'] = bb.bollinger_wband()
        ao = ta.momentum.AwesomeOscillatorIndicator(high=reshaped_df['high'], low=reshaped_df['low'])
        reshaped_df['AO'] = ao.ao()
        return reshaped_df

    def can_sell(self, df):
        ema_xb_bb_mavg = crossed_below(df['EMA_3'], df['BB_MAVG'])
        ao_xb_zero = (df.shift(2)['AO'] > 0) & (df.shift(-1)['AO'] < 0)
        vol_above_zero = df['volume'] > 0
        result = ema_xb_bb_mavg & ao_xb_zero & vol_above_zero
        return bool(result[-1])

    def can_buy(self, df):
        ema_xa_bb_mavg = crossed_above(df['EMA_3'], df['BB_MAVG'])
        ao_xo_zero = (df.shift(2)['AO'] < 0) & (df.shift(1)['AO'] > 0)
        vol_above_zero = df['volume'] > 0
        result = ema_xa_bb_mavg & ao_xo_zero & vol_above_zero
        return bool(result[-1])

    def alert_message(self, df):
        prev_candle = self.candle(df)
        last_close = prev_candle['close']
        last_ao = prev_candle['AO']
        return "Close: {:.2f}, Awesome Oscillator value: {:.2f}".format(
            last_close,
            last_ao
        ),
