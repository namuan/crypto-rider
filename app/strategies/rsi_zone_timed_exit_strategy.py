from app.strategies.base_strategy import BaseStrategy


class RsiZoneTimedExitStrategy(BaseStrategy):
    def __init__(self, locator, params=dict()):
        BaseStrategy.__init__(self, locator)
        self.rsi = params.get("rsi") or 4
        self.rsi_indicator = "rsi_{}".format(self.rsi)
        self.rsi_buy_limit = params.get("rsi_buy_limit") or 10
        self.rsi_sell_limit = params.get("rsi_sell_limit") or 55
        self.trend_indicator = params.get("trend_indicator") or "close_200_sma"
        self.candles_wait_before_sell = params.get("candles_wait_before_sell") or 1

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        _ = df[self.rsi_indicator]
        _ = df[self.trend_indicator]
        return df

    def can_buy(self, df):
        candle = self.candle(df)
        return [
            candle["close"] > candle[self.trend_indicator],
            candle[self.rsi_indicator] < self.rsi_buy_limit,
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
        return "Close {}, RSI({}) {}, Trend {}".format(
            candle["close"],
            self.rsi,
            candle[self.rsi_indicator],
            candle[self.trend_indicator],
        )

    def _candles_since_position_opened(self, current_position, df, n):
        return df.index[-1 + (-n)] == current_position.open_dt
