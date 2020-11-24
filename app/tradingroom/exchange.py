from app.config.basecontainer import BaseContainer
import logging


class Exchange(BaseContainer):
    def __init__(self, locator):
        BaseContainer.__init__(self, locator)

    def place_order(self, trade_order):
        logging.info("Placing trade in exchange: {}".format(trade_order))
