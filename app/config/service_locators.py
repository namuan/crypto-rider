import redis

from app.models import db
from app.notifiers.telegram_notifier import TelegramNotifier
from app.providers.market_data_provider import MarketDataProvider
from app.publishers.redis_publisher import RedisPublisher
from app.storage.alert_data_store import AlertDataStore
from app.storage.market_data_store import MarketDataStore
from app.strategies.strategy_runner import StrategyRunner


class ServiceLocator:
    objects = {}
    services = {}

    def __init__(self):
        self.services = dict(redis=redis.StrictRedis(), database=db)
        self.objects = dict(
            redis_publisher=RedisPublisher(self),
            market_data_provider=MarketDataProvider(self),
            market_data_store=MarketDataStore(self),
            alert_data_store=AlertDataStore(self),
            telegram_notifier=TelegramNotifier(self),
            strategy_runner=StrategyRunner(self),
        )

    def o(self, service):
        return self.objects.get(service)

    def s(self, infra_service):
        return self.services.get(infra_service)


locator = ServiceLocator()
