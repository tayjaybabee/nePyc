from argparse import ArgumentParser


class Arguments(ArgumentParser):
    def __init__(self):
        super().__init__(prog='nepyc', description='Information about the nePyc image sharing system.')
        self.add_argument('--version', action='store_true', help='Print version information.', default=False)
        self.__parsed = None

    @property
    def parsed(self):

        if not self.__parsed:
            self.__parsed = self.parse_args()

        return self.__parsed

    def parse_args(self):
        if not self.__parsed:
            return super().parse_args()
        else:
            return self.__parsed
