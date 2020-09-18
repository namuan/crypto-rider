import os

from peewee import *

home_dir = os.getenv("HOME")
db = SqliteDatabase(home_dir + "/crypto_rider_candles.db")


class CandleStick(Model):
    id = UUIDField(primary_key=True)
    exchange = CharField()
    timestamp = BigIntegerField()
    symbol = CharField()
    open = FloatField()
    high = FloatField()
    low = FloatField()
    close = FloatField()
    volume = FloatField()

    class Meta:
        database = db
        indexes = ((("timestamp", "exchange", "symbol"), True),)


CandleStick.create_table()
