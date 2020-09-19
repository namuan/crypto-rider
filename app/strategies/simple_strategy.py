from app.strategies.base_strategy import BaseStrategy


class SimpleStrategy(BaseStrategy):
    def apply(self):
        df = self.load_df(limit=300)
        signal = self.calculate_signal(df)
        if signal:
            self.alert("Higher Close(Prev {}, Current {})".format(self.prev_close(df), self.close(df)))

    def calculate_signal(self, df):
        if self.prev_close(df) < self.close(df):
            return True
        else:
            return False

    def close(self, df):
        return self.candle(df)['close']

    def prev_close(self, df):
        return self.candle(df, rewind=1)['close']
