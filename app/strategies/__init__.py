from app.config.service_locators import locator
from app.strategies.simple_strategy import SimpleStrategy
from app.strategies.ma_xb_strategy import MaCrossBelowStrategy

all_strategies = [
    # SimpleStrategy(locator),
    MaCrossBelowStrategy(locator)
]
