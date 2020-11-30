import talib as ta

from app.strategies.base_strategy import BaseStrategy


class CandleThreeBlackCrowsDojiTimedExitStrategy(BaseStrategy):
    def __init__(self, locator, params=dict()):
        BaseStrategy.__init__(self, locator)
        self.ll_candles = params.get("ll_candles") or 3
        self.avg_vol_mulp = params.get("avg_vol_mulp") or 1.5
        self.trend_indicator = params.get("trend_indicator") or "close_200_sma"
        self.candles_wait_before_sell = params.get("candles_wait_before_sell") or 1

    def title_suffix(self):
        return "LL Candles: {}, Avg Vol Mulp: {}, Sell after {} days".format(
            self.ll_candles,
            self.avg_vol_mulp,
            self.candles_wait_before_sell
        )

    def _determine_cdl_signal(self, df):
        bar_1 = df.shift(periods=4)
        bar_2 = df.shift(periods=3)
        bar_3 = df.shift(periods=2)
        bar_4 = df
        df['bar_1_closes_down'] = bar_1['open'] > bar_1['close']
        df['bar_2_ll'] = (bar_2['open'] < bar_1['open']) & (bar_2['close'] < bar_1['close'])
        df['bar_2_closes_down'] = bar_2['open'] > bar_2['close']
        df['bar_3_ll'] = (bar_3['open'] < bar_2['open']) & (bar_3['close'] < bar_2['close'])
        df['bar_3_closes_down'] = bar_3['open'] > bar_3['close']
        df['bar_4_ll'] = (bar_4['open'] < bar_3['open']) & (bar_4['close'] < bar_3['close'])
        df['bar_4_closes_down'] = bar_4['open'] > bar_4['close']
        return df['bar_4_closes_down'] \
               & df['bar_4_ll'] \
               & df['bar_3_closes_down'] \
               & df['bar_3_ll'] \
               & df['bar_2_closes_down'] \
               & df['bar_2_ll']

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        df['signal'] = self._determine_cdl_signal(df)
        df['CDLDOJI'] = ta.CDLDOJI(df.open, df.high, df.low, df.close)
        _ = df[self.trend_indicator]
        return df

    def can_buy(self, df):
        candle = self.candle(df)
        return [
            candle["close"] > candle[self.trend_indicator],
            candle['signal'],
            candle["CDLDOJI"] == 100,
        ]

    def can_sell(self, df):
        current_position = self.position()
        return [
            self._candles_since_position_opened(
                current_position, df, self.candles_wait_before_sell
            )
        ]

    def alert_message(self, df):
        candle = self.candle(df)
        return "Close {}, Trend {}".format(
            candle["close"],
            candle[self.trend_indicator],
        )

    def _candles_since_position_opened(self, current_position, df, n):
        return df.index[-1 + (-n)] == current_position.open_dt
