import logging
from threading import Thread

from app.config import ALERTS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import TradeOrder, last_trade_order, orders_df_from_database


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
        trade_order = last_trade_order(event.get("market"))
        if not trade_order and event.get("alert_type") == "BUY":
            logging.info("No existing trade found. Saving new order: {}".format(event))
            self._save_new_order(event)
        elif trade_order and not trade_order.is_open and event.get("alert_type") == "BUY":
            logging.info("Existing closed trade found and alert type is BUY. Saving new order: {}".format(event))
            self._save_new_order(event)
        elif trade_order and trade_order.is_open and event.get("alert_type") == "SELL":
            logging.info("Existing open trade found and alert type is SELL. Saving new order: {}".format(event))
            self._close_existing_order(trade_order, event)
        else:
            logging.info("Ignoring Trade Order: {}, Last Trade: {}".format(event, trade_order))

    def fetch_data(self):
        return orders_df_from_database()

    def force_close(self, market, dt_since, dt_to):
        trade_order = last_trade_order(market)
        if trade_order and trade_order.is_open:
            market_data_df = self.lookup_object("market_data_store").fetch_data(market, dt_since, dt_to)
            ts_last_candle = market_data_df["timestamp"].iloc[-1]
            last_close = market_data_df["close"].iloc[-1]
            logging.info("Force closing order at {}".format(last_close))
            trade_order.sell_timestamp = ts_last_candle
            trade_order.sell_price = last_close
            trade_order.sell_reason = "force close"
            trade_order.is_open = False
            trade_order.save()

    def _save_new_order(self, event):
        TradeOrder.save_from(dict(
            strategy=event.get("strategy"),
            buy_timestamp=event.get("timestamp"),
            market=event.get("market"),
            buy_price=event.get("close_price"),
            is_open=True,
        ))

    def _close_existing_order(self, trade_order, event):
        trade_order.sell_timestamp = event.get("timestamp")
        trade_order.sell_price = event.get("close_price")
        trade_order.sell_reason = event.get("strategy signal")
        trade_order.is_open = False
        trade_order.save()
