import json
import uuid
import pandas as pd
import numpy as np
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


def crossed(series1, series2, direction=None):
    if isinstance(series1, np.ndarray):
        series1 = pd.Series(series1)

    if isinstance(series2, (float, int, np.ndarray, np.integer, np.floating)):
        series2 = pd.Series(index=series1.index, data=series2)

    if direction is None or direction == "above":
        above = pd.Series((series1 > series2) & (series1.shift(1) <= series2.shift(1)))

    if direction is None or direction == "below":
        below = pd.Series((series1 < series2) & (series1.shift(1) >= series2.shift(1)))

    if direction is None:
        return above or below

    return above if direction == "above" else below


def crossed_above(series1, series2):
    return crossed(series1, series2, "above")


def crossed_below(series1, series2):
    return crossed(series1, series2, "below")


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
