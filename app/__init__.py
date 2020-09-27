import click

from app.config import init_logger
from app.config.service_locators import locator
from app.strategies import all_strategies

init_logger()


@click.group()
def cli():
    click.echo("#### Crypto-Rider ####")


@cli.command()
@click.option("--skip-wait", is_flag=True)
def data_provider(skip_wait):
    # Setup everything waiting for events
    market_data_store = locator.o("market_data_store")
    market_data_store.start()
    alert_data_store = locator.o("alert_data_store")
    alert_data_store.start()

    # Initialise all strategies
    for strategy in all_strategies:
        strategy.start()

    # Start notifiers
    telegram_notifier = locator.o("telegram_notifier")
    telegram_notifier.start()

    # Start feeding
    market_data_provider = locator.o("market_data_provider")
    market_data_provider.start(skip_wait)
