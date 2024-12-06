from typing import Union, Optional
from nepyc.log_engine import ROOT_LOGGER as PARENT_LOGGER


MOD_LOGGER = PARENT_LOGGER.get_child('server.utils.strings')


def string_too_long(string, max_length: int = 0, raise_if_true: bool = False):
    err_msg = f'The provided string contains too many characters. The maximum is {max_length}. It contains '\
              f'{len(string)} characters.'


    if len(string) > max_length:
        if raise_if_true:
            raise ValueError(err_msg)

        return True

    return False


def string_too_short(string, min_length: int = 1, raise_if_true: bool = False):
    err_msg = f'The provided string contains too few characters. The minimum is {min_length}. It contains '\
              f'{len(string)} characters.'


    if len(string) < min_length:
        if raise_if_true:
            raise ValueError(err_msg)

        return True

    return False


def string_in_list(string, list_of_strings: list[str], raise_if_true: bool = False):
    if string not in list_of_strings:
        err_msg = f'The provided string is not in the list of acceptable strings: {", ".join(list_of_strings)}'

        if raise_if_true:
            raise ValueError(err_msg)

        return True

    return False


def check_string_length(string, min_length: int = 1, max_length: int = 0):
    if not max_length in [0, None]:
        try:
            string_too_long(string, max_length, raise_if_true=True)
        except ValueError as e:
            raise e from e

    if not min_length in [0, None]:
        try:
            string_too_short(string, min_length, raise_if_true=True)
        except ValueError as e:
            raise e from e


def check_string(
        string,
        min_length:             int       = 1,
        max_length:             int       = 0,
        must_be_one_of:         list[str] = None,
        must_not_be_one_of:     list[str] = None,
        case_insensitive:       bool      = False,
        include_reason_on_fail: bool      = False
    ) -> Union[bool, tuple[bool, str]]:
    """
    Check if a string meets certain criteria.

    Note:
        The first check that this function performs is a type check. If the string is not a string, it will return False.

    Parameters:

        string (str):
            The string to check.

        min_length (int, optional):
            The minimum length of the string. Default is 1.

        max_length (int, optional):
            The maximum length of the string. Default is 0 (no maximum).

        must_be_one_of (list[str], optional):
            A list of strings that the string must be one of. Default is None.

        must_not_be_one_of (list[str], optional):
            A list of strings that the string must not be one of. Default is None.

        case_insensitive (bool, optional):
            Whether or not to perform the checks case-insensitively. Default is False.

        include_reason_on_fail (bool, optional):
            Whether or not to include a reason on a failed check. Default is False. If True, the function will return a
            tuple of (False, reason) instead of just False.

    Returns:
        bool or tuple[bool, str]:
            If the string meets the criteria, return True. Otherwise, return False. If `include_reason_on_fail` is :bool:`True`,
            return a tuple of (False, reason).

    """
    _log = MOD_LOGGER.get_child('check_string')

    def return_false(reason: Optional[str] = None):
        __log = _log.get_child('return_false')

        if include_reason_on_fail:
            __log.debug('Include reason on failure...')

            if reason is None:
                __log.debug('Was not given a reason, using generic reason.')
                reason = 'The string did not meet the criteria.'

            return False, reason

        return False

    log = _log

    # Check if the string is a string
    if not isinstance(string, str):
        log.error(f'The input must be a string. It is a {type(string)}')
        return_false('The input must be a string.')

    check_string_length(string, min_length, max_length=max_length)

    if case_insensitive:
        string = string.lower()
        must_be_one_of = [s.lower() for s in must_be_one_of] if must_be_one_of else None
        must_not_be_one_of = [s.lower() for s in must_not_be_one_of] if must_not_be_one_of else None

    # Check if the string must be one of a list of strings
    if must_be_one_of and string not in must_be_one_of:
        return_false(f'The string must be one of the following: {", ".join(must_be_one_of)}')

    # Check if the string must not be one of a list of strings
    if must_not_be_one_of and string in must_not_be_one_of:
        return_false(f'The string must not be one of the following: {", ".join(must_not_be_one_of)}')

    return True
