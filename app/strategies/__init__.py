from app.config.service_locators import locator
from app.strategies.simple_strategy import SimpleStrategy
from app.strategies.ma_xo_strategy import MaCrossOverStrategy

all_strategies = [
    # SimpleStrategy(locator),
    MaCrossOverStrategy(locator)
]
