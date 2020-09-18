import json


class RedisPublisher:
    def __init__(self, locator):
        self.locator = locator

    def channel_name(self, exchange, symbol):
        return "{}-{}".format(exchange, symbol)

    def publish_data(self, exchange, name, data):
        channel_name = self.channel_name(exchange, name)
        print("Channel: {} - Publishing {}".format(channel_name, data))
        self.locator.s('redis').publish(channel_name, json.dumps(data))
