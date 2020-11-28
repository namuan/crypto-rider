import logging

import pandas as pd

from app.config import ORDERS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import TradeOrder


class OrderDataStore(BaseContainer):
    def __init__(self, locator):
        BaseContainer.__init__(self, locator)

    def clear_data(self):
        TradeOrder.delete().execute()

    def fetch_data(self, strat_name):
        query = TradeOrder.select().where(
            TradeOrder.strategy == strat_name
        )
        return pd.DataFrame(list(query.dicts()))

    def fetch_data_with_strategy(self, strategy):
        query = TradeOrder.select().where(TradeOrder.strategy == strategy)
        return pd.DataFrame(list(query.dicts()))

    # Move to Broker
    def force_close(self, market, strategy, dt_since, dt_to):
        trade_order = self.last_trade_order(market, strategy)
        logging.info(
            "Force close order for {}/{} => {}".format(market, strategy, trade_order)
        )
        if trade_order and trade_order.is_open:
            market_data_df = self.lookup_object("market_data_store").fetch_data_between(
                market, dt_since, dt_to
            )
            ts_last_candle = market_data_df["timestamp"].iloc[-1]
            last_close = market_data_df["close"].iloc[-1]
            logging.info("Force closing order at {}".format(last_close))
            trade_order.sell_timestamp = ts_last_candle
            trade_order.sell_price = last_close
            trade_order.sell_reason = "force close"
            trade_order.is_open = False
            trade_order.save()

            self.lookup_object("redis_publisher").publish_data(
                ORDERS_CHANNEL, trade_order.to_event()
            )

    def save_new_order(self, event):
        order_event = dict(
            strategy=event.get("strategy"),
            buy_timestamp=event.get("timestamp"),
            market=event.get("market"),
            buy_price=event.get("close_price"),
            is_open=True,
        )
        self.lookup_object("redis_publisher").publish_data(ORDERS_CHANNEL, order_event)
        TradeOrder.save_from(order_event)
        return TradeOrder.get_by_id(order_event["id"])

    def close_existing_order(self, trade_order, event):
        trade_order.sell_timestamp = event.get("timestamp")
        trade_order.sell_price = event.get("close_price")
        trade_order.sell_reason = "sell signal"
        trade_order.is_open = False
        trade_order.save()

        self.lookup_object("redis_publisher").publish_data(
            ORDERS_CHANNEL, trade_order.to_event()
        )
        return trade_order

    def last_trade_order(self, market, strategy) -> TradeOrder:
        logging.info(
            "Getting last trade order for market {}, strategy {}".format(
                market, strategy
            )
        )
        return (
            TradeOrder.select()
                .where(TradeOrder.market == market, TradeOrder.strategy == strategy)
                .order_by(TradeOrder.buy_timestamp.desc())
                .first()
        )
