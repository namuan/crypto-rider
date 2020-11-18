import logging
import os

import pandas as pd
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

    class Meta:
        database = db

    @staticmethod
    def event(timestamp, strategy, market, alert_type, message):
        return dict(
            timestamp=timestamp,
            strategy=strategy,
            market=market,
            alert_type=alert_type,
            message=message,
        )

    @staticmethod
    def save_from(event):
        event["id"] = uuid_gen()
        SignalAlert.insert(event).execute()


def df_from_database(market, timestamp, limit):
    logging.info(
        "Getting last {} entries for market {} from database from {}".format(
            limit, market, timestamp
        )
    )
    query = (
        CandleStick.select()
        .where(CandleStick.market == market, CandleStick.timestamp <= timestamp)
        .order_by(CandleStick.timestamp.desc())
        .limit(limit)
    )
    df = pd.DataFrame(list(query.dicts()))
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


CandleStick.create_table()
SignalAlert.create_table()
