import logging

import pandas as pd

from app.common import wrap
from app.config.basecontainer import BaseContainer
from app.models import SignalAlert


class AlertDataStore(BaseContainer):
    def clear_data(self):
        SignalAlert.delete().execute()

    def fetch_data(self):
        query = SignalAlert.select()
        df = pd.DataFrame(list(query.dicts()))
        if not df.empty:
            df["date"] = pd.to_datetime(df["timestamp"], unit="ns")
        return wrap(df)

    def save_alert(self, event):
        logging.info("Saving Alert: {}".format(event))
        SignalAlert.save_from(event)
