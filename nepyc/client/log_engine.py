from nepyc.client.config.env import EnvConfig
from inspy_logger import InspyLogger, Loggable


CLIENT_LOGGER = InspyLogger('nePyc.client', console_level=EnvConfig.DEFAULTS['log_level'], no_file_logging=True)
