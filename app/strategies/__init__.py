from app.config.service_locators import locator
from app.strategies.simple_strategy import SimpleStrategy

all_strategies = [SimpleStrategy(locator)]
