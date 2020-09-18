import redis

from app.models import db
from app.providers.market_data_provider import MarketDataProvider
from app.publishers.redis_publisher import RedisPublisher
from app.storage.market_data_store import MarketDataStore


class ServiceLocator:
    objects = {}
    services = {}

    def __init__(self):
        self.services = dict(
            redis=redis.StrictRedis(),
            database=db
        )
        self.objects = dict(
            redis_publisher=RedisPublisher(self),
            market_data_provider=MarketDataProvider(self),
            market_data_store=MarketDataStore(self)
        )

    def o(self, service):
        return self.objects.get(service)

    def s(self, infra_service):
        return self.services.get(infra_service)


locator = ServiceLocator()
