import click

from app.config.service_locators import locator


@click.group()
def cli():
    click.echo("Crypto Rider")


@cli.command()
def data_provider():
    click.echo("Publish Market Data")
    market_data_provider = locator.s('market_data_provider')
    market_data_provider.start()
