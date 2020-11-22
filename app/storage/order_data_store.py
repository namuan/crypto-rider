import logging
from threading import Thread

import pandas as pd

from app.config import ALERTS_CHANNEL, ORDERS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import TradeOrder


class OrderDataStore(Thread, BaseContainer):
    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator, subscription_channel=ALERTS_CHANNEL)
        self.daemon = True

    def run(self):
        for event in self.pull_event():
            self.save_trade_order(event)

    def clear_data(self):
        TradeOrder.delete().execute()

    def save_trade_order(self, event):
        trade_order = self.last_trade_order(event.get("market"), event.get("strategy"))
        if not trade_order and event.get("alert_type") == "BUY":
            logging.info("No existing trade found. Saving new order: {}".format(event))
            self._save_new_order(event)
        elif (
                trade_order and not trade_order.is_open and event.get("alert_type") == "BUY"
        ):
            logging.info(
                "Existing closed trade found and alert type is BUY. Saving new order: {}".format(
                    event
                )
            )
            self._save_new_order(event)
        elif trade_order and trade_order.is_open and event.get(
                "alert_type") == "SELL" and self.is_selling_with_same_strategy(trade_order, event):
            logging.info(
                "Existing open trade found and alert type is SELL. Saving new order: {}".format(
                    event
                )
            )
            self._close_existing_order(trade_order, event)
        else:
            logging.info(
                "Ignoring Trade Order: {}, Last Trade: {}".format(event, trade_order)
            )

    def is_selling_with_same_strategy(self, open_order, new_event):
        last_open_order_strategy = open_order.strategy
        current_strategy = new_event.get("strategy")
        if last_open_order_strategy == current_strategy:
            return True
        else:
            logging.info("Ignoring SELL alert as open order strategy {} doesn't match with current strategy {}".format(
                last_open_order_strategy,
                current_strategy
            ))
            return False

    def fetch_data(self):
        query = TradeOrder.select()
        return pd.DataFrame(list(query.dicts()))

    def fetch_data_with_strategy(self, strategy):
        query = TradeOrder.select().where(
            TradeOrder.strategy == strategy
        )
        return pd.DataFrame(list(query.dicts()))

    def force_close(self, market, strategy, dt_since, dt_to):
        trade_order = self.last_trade_order(market, strategy)
        logging.info("Force close order for {}/{} => {}".format(
            market,
            strategy,
            trade_order
        ))
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

            self.lookup_object("redis_publisher").publish_data(ORDERS_CHANNEL, trade_order.to_event())

    def _save_new_order(self, event):
        order_event = dict(
            strategy=event.get("strategy"),
            buy_timestamp=event.get("timestamp"),
            market=event.get("market"),
            buy_price=event.get("close_price"),
            is_open=True,
        )
        self.lookup_object("redis_publisher").publish_data(ORDERS_CHANNEL, order_event)
        TradeOrder.save_from(order_event)


    def _close_existing_order(self, trade_order, event):
        trade_order.sell_timestamp = event.get("timestamp")
        trade_order.sell_price = event.get("close_price")
        trade_order.sell_reason = "sell signal"
        trade_order.is_open = False
        trade_order.save()

        self.lookup_object("redis_publisher").publish_data(ORDERS_CHANNEL, trade_order.to_event())

    def last_trade_order(self, market, strategy) -> TradeOrder:
        logging.info("Last trade order for market {}, strategy {}".format(market, strategy))
        return (
            TradeOrder.select()
                .where(TradeOrder.market == market, TradeOrder.strategy == strategy)
                .order_by(TradeOrder.buy_timestamp.desc())
                .first()
        )
