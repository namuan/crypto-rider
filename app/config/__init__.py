import configparser
import logging


def config(section, key, default_value=None):
    c = configparser.ConfigParser()
    c.read("crypto.cfg")

    if not c.has_section(section):
        return default_value

    return c.get(section, key) or default_value


def providers_fetch_delay():
    return int(config("PROVIDERS", "FETCH_DELAY_IN_SECS", 60))


def provider_markets():
    all_markets = config('PROVIDERS', 'MARKETS')
    return all_markets.split(",")


def init_logger():
    handlers = [
        logging.StreamHandler(),
    ]

    logging.basicConfig(
        handlers=handlers,
        format="%(asctime)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )
    logging.captureWarnings(capture=True)
