from threading import Thread

from app.config import ALERTS_CHANNEL
from app.config.basecontainer import BaseContainer
from app.models import SignalAlert


class AlertDataStore(Thread, BaseContainer):
    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator, subscription_channel=ALERTS_CHANNEL)

    def run(self):
        for event in self.pull_event():
            SignalAlert.save_from(event)
