import logging

from app.bank import NotEnoughCashError
from app.config.basecontainer import BaseContainer


class Broker(BaseContainer):

    def execute_trade(self, alert_event):
        trade_order = self._setup_order(alert_event)
        if not trade_order:
            return

        try:
            self.lookup_object("account_manager").reserve(trade_order)
            self.lookup_object("exchange").place_order(trade_order)
            self.lookup_object("account_manager").confirm(trade_order)
        except NotEnoughCashError as e:
            logging.error("Not enough cash to place this trade", e)

    def _setup_order(self, alert_event):
        trade_order = self.lookup_object("order_data_store").last_trade_order(
            alert_event.get("market"), alert_event.get("strategy")
        )
        if not trade_order and alert_event.get("alert_type") == "BUY":
            logging.info(
                "No existing trade found. Saving new order: {}".format(alert_event)
            )
            return self.lookup_object("order_data_store").save_new_order(alert_event)
        elif (
                trade_order
                and not trade_order.is_open
                and alert_event.get("alert_type") == "BUY"
        ):
            logging.info(
                "Existing closed trade found and alert type is BUY. Saving new order: {}".format(
                    alert_event
                )
            )
            return self.lookup_object("order_data_store").save_new_order(alert_event)
        elif (
                trade_order
                and trade_order.is_open
                and alert_event.get("alert_type") == "SELL"
                and self.is_selling_with_same_strategy(trade_order, alert_event)
        ):
            logging.info(
                "Existing open trade found and alert type is SELL. Saving new order: {}".format(
                    alert_event
                )
            )
            return self.lookup_object("order_data_store").close_existing_order(
                trade_order, alert_event
            )
        else:
            logging.info(
                "Ignoring Trade Order: {}, Last Trade: {}".format(
                    alert_event, trade_order
                )
            )
            return None

    def is_selling_with_same_strategy(self, open_order, new_event):
        last_open_order_strategy = open_order.strategy
        current_strategy = new_event.get("strategy")
        if last_open_order_strategy == current_strategy:
            return True
        else:
            logging.info(
                "Ignoring SELL alert as open order strategy {} doesn't match with current strategy {}".format(
                    last_open_order_strategy, current_strategy
                )
            )
            return False
