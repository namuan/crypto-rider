import redis

from app.bank.account_manager import AccountManager
from app.models import db
from app.notifiers.pushover_notifier import PushoverNotifier
from app.notifiers.telegram_notifier import TelegramNotifier
from app.providers.market_data_provider import MarketDataProvider
from app.publishers.redis_publisher import RedisPublisher
from app.publishers.report_publisher import ReportPublisher
from app.storage.alert_data_store import AlertDataStore
from app.storage.market_data_store import MarketDataStore
from app.storage.order_data_store import OrderDataStore
from app.strategies.strategy_runner import StrategyRunner
from app.tradingroom.broker import Broker
from app.tradingroom.exchange import Exchange


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
            pushover_notifier=PushoverNotifier(self),
            strategy_runner=StrategyRunner(self),
            report_publisher=ReportPublisher(self),
            order_data_store=OrderDataStore(self),
            account_manager=AccountManager(self),
            exchange=Exchange(self),
            broker=Broker(self),
        )

    def o(self, service):
        return self.objects.get(service)

    def s(self, infra_service):
        return self.services.get(infra_service)


locator = ServiceLocator()
