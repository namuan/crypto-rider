class RedisPublisher:
    def __init__(self, locator):
        self.locator = locator

    def publish_data(self, channel, data):
        print("Channel: {} - Publishing {}".format(channel, data))
