from app.strategies import MaCrossBelowStrategy
from app.config.service_locators import locator

s = MaCrossBelowStrategy(locator)
s.last_event = {'exchange': 'binance', 'market': 'BTC/USDT', 'timestamp': 1605371820000, 'open': 15975.86,
                'high': 15977.66, 'low': 15962.11, 'close': 15966.77, 'volume': 33.839882}
s.apply()
