from app.config.basecontainer import BaseContainer
import logging


class AccountManager(BaseContainer):
    def __init__(self, locator):
        BaseContainer.__init__(self, locator)

    def reserve(self, trade_order):
        logging.info("Reserving trade: {}".format(trade_order))

    def confirm(self, trade_order):
        logging.info("Confirming trade: {}".format(trade_order))
