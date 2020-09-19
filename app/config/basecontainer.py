import logging

from app.common import b2s, json_from_bytes


class BaseContainer:
    def __init__(self, locator, subscription_channel=None):
        self.locator = locator
        if subscription_channel:
            redis_instance = self.lookup_service("redis")
            self.channels = [subscription_channel]
            self.pubsub = redis_instance.pubsub()
            self.pubsub.subscribe(self.channels)

    def lookup_object(self, object_name):
        return self.locator.o(object_name)

    def lookup_service(self, service_name):
        return self.locator.s(service_name)

    def can_handle(self, item):
        return (
            item.get("type") == "message" and b2s(item.get("channel")) in self.channels
        )

    def pull_event(self):
        for item in self.pubsub.listen():
            try:
                if self.can_handle(item):
                    event = json_from_bytes(item.get("data"))
                    yield event
            except Exception as e:
                logging.error(e)
