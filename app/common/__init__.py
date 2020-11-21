import json
import uuid

from stockstats import StockDataFrame

UTF_ENCODING = "utf-8"


def b2s(src):
    """
    Convert from bytes to string
    :param src: bytes
    :return: string
    """
    return src.decode(encoding=UTF_ENCODING)


def json_from_bytes(src_bytes):
    s = b2s(src_bytes)
    return json.loads(s)


def uuid_gen():
    return uuid.uuid4()


def candle_event_name(exchange_id, timeframe):
    return "{}-ohlcv-{}".format(exchange_id, timeframe)


def normalise_market(market):
    return market.replace("/", "")


# https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
def reshape_data(df, timedelta):
    logic = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    return wrap(df.resample(timedelta).apply(logic))


def wrap(df):
    return StockDataFrame.retype(df)
