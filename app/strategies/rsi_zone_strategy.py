from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy
from datetime import timedelta
import mplfinance as mpf


class RsiZoneStrategy(BaseStrategy):
    rsi = 4
    rsi_indicator = "rsi_{}".format(rsi)
    rsi_buy_limit = 25
    rsi_sell_limit = 55
    trend_indicator = "close_200_sma"

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        reshaped_df = reshape_data(df, timedelta="4h")
        _ = reshaped_df[self.rsi_indicator]
        _ = reshaped_df[self.trend_indicator]
        return reshaped_df

    def can_buy(self, df):
        candle = self.candle(df)
        return [
            candle["close"] > candle[self.trend_indicator],
            candle[self.rsi_indicator] < self.rsi_buy_limit,
        ]

    def can_sell(self, df):
        candle = self.candle(df)
        return [candle[self.rsi_indicator] > self.rsi_sell_limit]

    def alert_message(self, df):
        candle = self.candle(df)
        return "Close {}, RSI({}) {}, Trend {}".format(
            candle["close"],
            self.rsi,
            candle[self.rsi_indicator],
            candle[self.trend_indicator],
        )

    def get_additional_plots(self, market, dt_since, dt_to):
        df = self.calculate_indicators()
        dt_end = dt_to - timedelta(days=1)
        return [
            mpf.make_addplot(
                df[self.trend_indicator][dt_since:dt_end], linestyle="dashed"
            ),
            mpf.make_addplot(
                df[self.rsi_indicator][dt_since:dt_end], linestyle="dashed", panel=2
            ),
        ]
