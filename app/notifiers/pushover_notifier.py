import logging
import os
from datetime import datetime
from threading import Thread

import requests
from dotenv import load_dotenv

from app.config import ORDERS_CHANNEL
from app.config.basecontainer import BaseContainer

load_dotenv()

PUSHOVER_URL = os.getenv("PUSHOVER_URL")
PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
PUSHOVER_USER = os.getenv("PUSHOVER_USER")


class PushoverNotifier(Thread, BaseContainer):
    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator, subscription_channel=ORDERS_CHANNEL)
        self.daemon = True

    def send_message(self, message):
        logging.info(message)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            'token': PUSHOVER_TOKEN,
            'user': PUSHOVER_USER,
            'title': 'CryptoRider',
            'message': message
        }
        requests.post(url=PUSHOVER_URL, headers=headers, data=data)

    def construct_message(self, event):
        buy_or_sell = "Bought" if event.get("is_open") else "Sold"
        buy_or_sell_ts = event.get("buy_timestamp") if event.get("is_open") else event.get("sell_timestamp")
        buy_or_sell_price = event.get("buy_price") if event.get("is_open") else event.get("sell_price")
        buy_or_sell_dt = datetime.fromtimestamp(int(buy_or_sell_ts) / 1000)
        return "{} {} FOR {} AT {}".format(
            buy_or_sell,
            event.get("market"),
            buy_or_sell_price,
            buy_or_sell_dt.strftime("%Y-%m-%d %H:%M:%S")
        )

    def run(self):
        for event in self.pull_event():
            print(event)
            alert_message = self.construct_message(event)
            self.send_message(alert_message)
