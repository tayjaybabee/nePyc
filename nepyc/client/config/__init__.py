from nepyc.client.cli.arguments import Arguments
from nepyc.client.config.env import EnvConfig, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_LOG_LEVEL
from nepyc.common.config.dirs import DEFAULT_DIRS
from pathlib import Path
from configparser import ConfigParser


class Args:
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    log_level = DEFAULT_LOG_LEVEL



DEFAULT_CONFIG_FILE_NAME = 'client_config.ini'
DEFAULT_CONFIG_FILE_PATH = DEFAULT_DIRS.user_config_path.joinpath(DEFAULT_CONFIG_FILE_NAME)


class Config:

    DEFAULTS = {
        'host': DEFAULT_HOST,
        'port': DEFAULT_PORT,
        'log_level': DEFAULT_LOG_LEVEL
    }

    def __init__(
            self,
            config_file_path: str  = DEFAULT_CONFIG_FILE_PATH,
            env_prefix:       str  = 'NEPYC_CLIENT_',
            defaults:         dict = None,
            skip_cli_args:    bool = False
    ):
        self.__args               = Args() if skip_cli_args else Arguments().parsed
        self.__config_file_path   = None
        self.__config_file_loaded = False
        self.__env_prefix         = None
        self.__defaults           = self.DEFAULTS
        self.__env_vars           = None
        self.__parser             = ConfigParser()
        self.__resolved           = False
        self.__skip_cli_args      = False

        self.skip_cli_args = skip_cli_args

        self.config_file_path = config_file_path

        self._load_config_sources()

        self._resolve_config()

    @property
    def cli_args(self):
        return self.__args

    @property
    def config_file_loaded(self):
        return self.__config_file_loaded

    @property
    def config_file_path(self):
        return self.__config_file_path

    @config_file_path.setter
    def config_file_path(self, new):
        if not isinstance(new, (str, Path)):
            raise TypeError(f'Invalid type ({type(new)}) for `config_file_path`. Value must be a string or Path!')

        if isinstance(new, str):
            new = Path(new).expanduser().resolve().absolute()

        self.__config_file_path = new

    @property
    def defaults(self):
        return self.__defaults

    @property
    def env_vars(self):
        return self.__env_vars

    @property
    def env_prefix(self):
        return self.__env_prefix

    @env_prefix.setter
    def env_prefix(self, new):
        if not isinstance(new, str):
            raise TypeError(f'Invalid type ({type(new)}) for `env_prefix`. Value must be a string!')

        if not new.endswith('_'):
            new = f'{new}_'

        self.__env_prefix = new

    @property
    def parser(self):
        return self.__parser

    @property
    def resolved(self):
        return self.__resolved

    @property
    def skip_cli_args(self):
        return self.__skip_cli_args

    @skip_cli_args.setter
    def skip_cli_args(self, new):
        if self.resolved:
            raise RuntimeError('Cannot change `skip_cli_args` after config has been resolved')

        if not isinstance(new, bool):
            raise TypeError(f'Invalid type ({type(new)}) for `skip_cli_args`. Value must be a boolean!')

        self.__skip_cli_args = new

    def _load_config_file(self):
        if self.config_file_path.exists():
            self.parser.read(self.config_file_path)

    def _load_config_sources(self):
        self._load_defaults()
        self._load_config_file()
        self._load_env_vars()
        #self._parse_args()

    def _load_defaults(self):
        self._final_config = dict(self.defaults)

    def _load_env_vars(self):
        if self.__env_vars is None:
            self.__env_vars = EnvConfig(prefix=self.env_prefix)

    def _parse_args(self):
        if not self.skip_cli_args:
            from nepyc.client.cli.arguments import ARGS
            self.__args = ARGS.parsed

    def _resolve_config(self):
        self.host = (
            self.__args.host
            or self.env_vars.HOST
            or self.parser.get('USER', 'host', fallback=self.DEFAULTS['host'])
        )

        self.port = (
            self.__args.port
            or self.env_vars.PORT
            or self.parser.getint('USER', 'port', fallback=self.DEFAULTS['port'])
        )

        self.log_level = (
            self.__args.log_level
            or self.env_vars.LOG_LEVEL
            or self.parser.get('USER', 'log_level', fallback=self.DEFAULTS['log_level'])
        )

        self.__resolved = True

    def save(self):
        with self.config_file_path.open('w') as f:
            self.parser.write(f)

    def load(self):
        self._load_config_file()
