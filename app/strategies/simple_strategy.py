from app.common import reshape_data
from app.strategies.base_strategy import BaseStrategy


class SimpleStrategy(BaseStrategy):

    def calculate_indicators(self):
        df = self.load_df(limit=1000)
        reshaped_df = reshape_data(df, timedelta="1d")
        return reshaped_df

    def can_sell(self, df):
        candle = self.candle(df)
        prev_candle = self.candle(df, rewind=-2)
        return prev_candle["close"] > candle["close"]

    def can_buy(self, df):
        candle = self.candle(df)
        prev_candle = self.candle(df, rewind=-2)
        return candle["close"] > prev_candle["close"]

    def alert_message(self, df):
        candle = self.candle(df)
        prev_candle = self.candle(df, rewind=-2)
        return "Close(Prev {}, Current {})".format(
            prev_candle["close"], candle["close"]
        )

    def get_additional_plots(self, market, dt_since, dt_to):
        return []
