import logging
import os
from datetime import datetime

import pandas as pd
from peewee import *

from app.common import uuid_gen, wrap

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
    def event(strategy, buy_timestamp, sell_timestamp, market, buy_price, sell_price, is_open, sell_reason):
        return dict(
            strategy=strategy,
            buy_timestamp=buy_timestamp,
            sell_timestamp=sell_timestamp,
            market=market,
            buy_price=buy_price,
            sell_price=sell_price,
            is_open=is_open,
            sell_reason=sell_reason,
        )

    @staticmethod
    def save_from(event):
        event["id"] = uuid_gen()
        TradeOrder.insert(event).execute()


def last_trade_order(market):
    logging.info("Getting last trade order for market: {}".format(market))
    return (
        TradeOrder.select()
            .where(TradeOrder.market == market)
            .order_by(TradeOrder.buy_timestamp.desc())
            .first()
    )


def market_data(market, ts, limit):
    logging.info(
        "Getting last {} entries for market {} from database from {} => {}".format(
            limit, market, ts, datetime.fromtimestamp(ts / 1000)
        )
    )
    query = (
        CandleStick.select()
            .where(CandleStick.market == market, CandleStick.timestamp <= ts)
            .order_by(CandleStick.timestamp.desc())
            .limit(limit)
    )
    df = pd.DataFrame(list(query.dicts()))
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    return wrap(df)


def market_data_between(market, ts_from, ts_to):
    logging.info(
        "Getting entries for market {} from database from {} => {}".format(
            market, ts_from, ts_to
        )
    )
    query = (
        CandleStick.select()
            .where(CandleStick.market == market, CandleStick.timestamp >= ts_from, CandleStick.timestamp <= ts_to)
    )
    df = pd.DataFrame(list(query.dicts()))
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
    return wrap(df)


def alerts_df_from_database():
    query = (
        SignalAlert.select()
    )
    df = pd.DataFrame(list(query.dicts()))
    df["date"] = pd.to_datetime(df["timestamp"], unit="ns")
    return wrap(df)


def orders_df_from_database():
    query = (
        TradeOrder.select()
    )
    return pd.DataFrame(list(query.dicts()))


CandleStick.create_table()
SignalAlert.create_table()
TradeOrder.create_table()
