from app.config.service_locators import locator
from app.strategies.simple_strategy import SimpleStrategy
from app.strategies.ma_xo_strategy import MaCrossOverStrategy
from app.strategies.ema_bb_alligator_strategy import EMABBAlligatorStrategy

all_strategies = [
    # SimpleStrategy(locator),
    MaCrossOverStrategy(locator),
    EMABBAlligatorStrategy(locator)
]
