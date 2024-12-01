from nepyc.server.config import CONFIG
from inspy_logger import InspyLogger, Loggable


ROOT_LOGGER = InspyLogger('nepyc', console_level=CONFIG.LOG_LEVEL, no_file_logging=True)
