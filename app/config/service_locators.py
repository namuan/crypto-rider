from app.providers.market_data_provider import MarketDataProvider
from app.publishers.redis_publisher import RedisPublisher

class ServiceLocator:
    services = {}

    def __init__(self):
        self.services = dict(
            redis_publisher=RedisPublisher(self),
            market_data_provider=MarketDataProvider(self),
        )

    def s(self, service):
        return self.services.get(service, None)


locator = ServiceLocator()
