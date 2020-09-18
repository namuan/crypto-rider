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


CandleStick.create_table()
