import sys
from nepyc.client.config import Config
from nepyc.client.client import ImageClient
from nepyc.client.log_engine import CLIENT_LOGGER as ROOT_LOGGER
from nepyc.common.about.version import PYPI_VERSION_INFO


CONFIG = Config(skip_cli_args=False)

ARGS = CONFIG.cli_args

ROOT_LOGGER.set_level(console_level=CONFIG.log_level)

APP_LOGGER = ROOT_LOGGER.get_child('Client')

APP_LOGGER.set_level(console_level=ARGS.log_level)



def main():
    log = APP_LOGGER.get_child('main')
    client = ImageClient(
        host=CONFIG.host,
        port=int(CONFIG.port),
    )

    try:
        log.debug(f'Connecting to {client.host}:{client.port}')
        client.connect()
        log.debug(f'Connected to {client.host}:{client.port}')
    except ConnectionRefusedError:
        log.error(f'Unable to connect to {client.host}:{client.port}')
        sys.exit(1)


    client.send_image(ARGS.image_path)

    client.close()
