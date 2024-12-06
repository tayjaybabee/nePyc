from nepyc.server.cli.config import ENV_CONFIG as CONFIG
from inspy_logger import InspyLogger, Loggable


ROOT_LOGGER = InspyLogger('nepyc', console_level=CONFIG.LOG_LEVEL, no_file_logging=True)


ROOT_LOGGER.instances['inSPy-Logger'].set_level(console_level='info')
