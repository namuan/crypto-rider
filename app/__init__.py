import click

from app.config.service_locators import locator


@click.group()
def cli():
    click.echo("Crypto Rider")


@cli.command()
def data_provider():
    click.echo("Publish Market Data")
    # Setup everything waiting for events
    market_data_store = locator.o("market_data_store")
    market_data_store.start()

    # Start feeding
    market_data_provider = locator.o("market_data_provider")
    market_data_provider.start()
