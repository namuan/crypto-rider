import logging
from threading import Thread

from app.config import ALERTS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import SignalAlert


class AlertDataStore(Thread, BaseContainer):
    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator, subscription_channel=ALERTS_CHANNEL)
        self.daemon = True

    def run(self):
        for event in self.pull_event():
            self.save_alert(event)

    def clear_data(self):
        SignalAlert.delete().execute()

    def save_alert(self, event):
        logging.info("Saving Alert: {}".format(event))
        SignalAlert.save_from(event)
