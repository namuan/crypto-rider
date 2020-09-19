import logging

from app.strategies.base_strategy import BaseStrategy


class SimpleStrategy(BaseStrategy):
    def apply(self, event):
        logging.info("Running {} - Received event {}".format(self.__class__, event))
