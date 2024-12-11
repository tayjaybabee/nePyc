from nepyc.client.config.env import EnvConfig
from argparse import ArgumentParser
from nepyc.client.about import DESCRIPTION, PROG_NAME


ENV_CONFIG = EnvConfig()


class Arguments(ArgumentParser):
    def __init__(self):
        super().__init__(prog=PROG_NAME, description=DESCRIPTION)

        self.__parsed = None

        self.add_argument('image_path', help='Path to the image to be uploaded', type=str, action='store')

        self.add_argument('-H', '--host', default=ENV_CONFIG.host)
        self.add_argument('-P', '--port', default=ENV_CONFIG.port)
        self.add_argument('-L', '--log-level', default=ENV_CONFIG.log_level)
        self.add_argument('-C', '--config-file', default=ENV_CONFIG.config_file_path)
        self.add_argument('-V', '--version', action='store_true')

    @property
    def parsed(self):
        if not self.__parsed:
            self.__parsed = self.parse_args()

        return self.__parsed
