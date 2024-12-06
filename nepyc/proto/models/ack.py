from nepyc.server.utils.strings import check_string


class Ack:
    def __init__(
            self,
            code,
            status,
            description,
            children=None
    ):
        self.__code        = None
        self.__status      = None
        self.__description = None
        self.__children    = None

    @property
    def children(self):
        return self.__children

    @property
    def code(self):
        return self.__code

    @code.setter
    def code(self, new):
        if not self.__code and isinstance(new, int):

            self.__code = new

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, new):
        if not self.__descritpion:
            str_res = check_string(new, include_reason_on_fail=True)
        if not self.__description and check_string(new):
            self.__description = new
