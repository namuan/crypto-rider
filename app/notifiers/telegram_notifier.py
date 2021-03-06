import logging
import os
from datetime import datetime
from threading import Thread

import requests
from dotenv import load_dotenv

from app.common import normalise_market
from app.config import ALERTS_CHANNEL
from app.config.basecontainer import BaseContainer

load_dotenv()

CHAT_ID = os.getenv("CHAT_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")


class TelegramNotifier(Thread, BaseContainer):
    def __init__(self, locator):
        Thread.__init__(self)
        BaseContainer.__init__(self, locator, subscription_channel=ALERTS_CHANNEL)
        self.daemon = True

    def get_url(self, method, token):
        return "https://api.telegram.org/bot{}/{}".format(token, method)

    def send_message(self, message, format="Markdown"):
        logging.info(message)

        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": format,
            "disable_web_page_preview": True,
        }
        requests.post(self.get_url("sendMessage", BOT_TOKEN), data=data)

    def construct_message(self, event):
        ts = datetime.fromtimestamp(int(event.get("timestamp")) / 1000)
        return """{} -> **{}** {} signal at {}
{}
[TradingView](https://uk.tradingview.com/chart/?symbol=BINANCE%3A{})
""".format(
            event.get("strategy"),
            event.get("market"),
            event.get("alert_type"),
            ts.strftime("%Y-%m-%d %H:%M:%S"),
            event.get("message"),
            normalise_market(event.get("market")),
        )

    def run(self):
        for event in self.pull_event():
            alert_message = self.construct_message(event)
            self.send_message(alert_message)
