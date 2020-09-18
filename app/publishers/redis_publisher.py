import json
import logging

from app.config.basecontainer import BaseContainer


class RedisPublisher(BaseContainer):
    def channel_name(self, exchange, symbol):
        return "{}-{}".format(exchange, symbol)

    def publish_data(self, channel_name, data):
        logging.info("Channel: {} - Publishing {}".format(channel_name, data))
        self.lookup_service("redis").publish(channel_name, json.dumps(data))
