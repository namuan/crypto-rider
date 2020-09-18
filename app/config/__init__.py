import configparser


def config(section, key, default_value=None):
    c = configparser.ConfigParser()
    c.read('crypto.cfg')

    if not c.has_section(section):
        return default_value

    return c.get(section, key) or default_value


def providers_fetch_delay():
    return int(config('PROVIDERS', 'FETCH_DELAY_IN_SECS', 60))
