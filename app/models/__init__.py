import os

from peewee import *

from app.common import uuid_gen

home_dir = os.getenv("HOME")
db = SqliteDatabase(home_dir + "/crypto_rider_candles.db")


class CandleStick(Model):
    id = UUIDField(primary_key=True)
    exchange = CharField()
    timestamp = BigIntegerField()
    market = CharField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = FloatField()

    class Meta:
        database = db
        indexes = ((("timestamp", "exchange", "market"), True),)

    @staticmethod
    def event(exchange, market, ts, op, hi, lo, cl, vol):
        return dict(
            exchange=exchange,
            market=market,
            timestamp=ts,
            open=op,
            high=hi,
            low=lo,
            close=cl,
            volume=vol,
        )

    @staticmethod
    def save_from(event):
        event["id"] = uuid_gen()
        CandleStick.insert(event).on_conflict_ignore().execute()


class SignalAlert(Model):
    id = UUIDField(primary_key=True)
    strategy = CharField()
    timestamp = BigIntegerField()
    market = CharField()
    alert_type = CharField()
    message = CharField()
    close_price = FloatField()

    class Meta:
        database = db

    @staticmethod
    def event(timestamp, strategy, market, alert_type, message, close_price):
        return dict(
            timestamp=timestamp,
            strategy=strategy,
            market=market,
            alert_type=alert_type,
            message=message,
            close_price=close_price,
        )

    @staticmethod
    def save_from(event):
        event["id"] = uuid_gen()
        SignalAlert.insert(event).execute()


class TradeOrder(Model):
    id = UUIDField(primary_key=True)
    strategy = CharField()
    buy_timestamp = BigIntegerField()
    market = CharField()
    buy_price = FloatField()
    is_open = BooleanField()
    sell_timestamp = BigIntegerField(null=True)
    sell_price = FloatField(null=True)
    sell_reason = CharField(null=True)

    class Meta:
        database = db

    @staticmethod
    def event(
        strategy,
        buy_timestamp,
        sell_timestamp,
        market,
        buy_price,
        sell_price,
        is_open,
        sell_reason,
    ):
        return dict(
            strategy=strategy,
            buy_timestamp=float(buy_timestamp),
            sell_timestamp=float(sell_timestamp),
            market=market,
            buy_price=float(buy_price),
            sell_price=float(sell_price),
            is_open=is_open,
            sell_reason=sell_reason,
        )

    def to_event(self):
        return TradeOrder.event(
            self.strategy,
            self.buy_timestamp,
            self.sell_timestamp,
            self.market,
            self.buy_price,
            self.sell_price,
            self.is_open,
            self.sell_reason
        )

    @staticmethod
    def save_from(event):
        event["id"] = uuid_gen()
        TradeOrder.insert(event).execute()


CandleStick.create_table()
SignalAlert.create_table()
TradeOrder.create_table()
