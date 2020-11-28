import io

import click
import sys
from dotmap import DotMap

ENCODE_IN = "utf-8"
ENCODE_OUT = "utf-8"

from app.config import init_logger
from app.config.service_locators import locator

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

    # Start feeding
    market_data_provider = locator.o("market_data_provider")
    market_data_provider.start(skip_wait)


@cli.command()
def strategy_runner():
    alert_data_store = locator.o("alert_data_store")
    alert_data_store.start()

    # Start notifiers
    telegram_notifier = locator.o("telegram_notifier")
    telegram_notifier.start()
    pushover_notifier = locator.o("pushover_notifier")
    pushover_notifier.start()

    # Strategy runner
    strategy_runner = locator.o("strategy_runner")
    strategy_runner.start()


@cli.command()
@click.option("--market", help="Market", required=True)
@click.option(
    "--data-file",
    help="JSON file with historical ohlcv data",
    required=True,
    type=lambda x: open(x, encoding=ENCODE_IN),
    default=io.TextIOWrapper(sys.stdin.buffer, encoding=ENCODE_IN),
)
def load_historical_data(market, data_file):
    market_data_store = locator.o("market_data_store")
    market_data_store.start()

    market_data_provider = locator.o("market_data_provider")
    market_data_provider.load_historical_data(market, data_file)


@cli.command()
@click.option("--market", help="Market", required=True)
@click.option("--since", help="Since", required=True)
def download_historical_data(market, since):
    market_data_store = locator.o("market_data_store")
    market_data_store.start()

    market_data_provider = locator.o("market_data_provider")
    market_data_provider.download_historical_data(market, since)


@cli.command()
@click.option("--market", help="Market", required=True)
@click.option("--since", help="Since", required=True)
@click.option("--to", help="To", required=True)
@click.option("--strats", help="Strategies to backtest. eg. StrategyA,StrategyB")
def back_test(market, since, to, strats):
    display_opts = DotMap({"trades": True, "alerts": False, "plots": False})
    strategy_runner = locator.o("strategy_runner")
    strategy_runner.run_back_test(market, since, to, strats, display_opts)
