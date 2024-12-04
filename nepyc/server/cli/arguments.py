"""
This module contains the Arguments class which is used to parse the command line arguments. The Arguments class is used
to parse the command line arguments and return a dictionary of the arguments.

Example Usage:
    >>> from nepyc.server.cli.arguments import Arguments
    >>> args = Arguments()
    >>> print(args.parsed)
    Namespace(host='localhost', port=8580)

    >>> args = Arguments.from_env()
    >>> print(args.parsed)
    Namespace(host='localhost', port=8580)
"""
from argparse import ArgumentParser
from os import environ


# Default values for the bind host and port
DEFAULT_BIND_HOST = 'localhost'
DEFAULT_BIND_PORT = 8580
DEFAULT_LOG_LEVEL = 'INFO'


class Arguments:
    """
    The Arguments class is used to parse the command line arguments and return a dictionary of the arguments. The class
    is used to parse the command line arguments and return a dictionary of the arguments.

    Example Usage:
        >>> args = Arguments()
        >>> print(args.parsed)
        Namespace(host='localhost', port=8580)
    """
    def __init__(self):
        """
        Create an instance of the class with the default values set.

        Returns:
            None

        Example Usage:
            >>> args = Arguments()
        """
        # Create the ArgumentParser object without any arguments
        self.parser = ArgumentParser()
        self.parser.add_argument('-H', '--host', default=DEFAULT_BIND_HOST, help='Address to bind to.')
        self.parser.add_argument('-P', '--port', type=int, default=DEFAULT_BIND_PORT, help='The port to bind to.')
        self.parser.add_argument('-L', '--log-level', default=DEFAULT_LOG_LEVEL, help='The level at which to log.')
        self.__parsed = None

    @property
    def parsed(self):
        """
        Parse the command line arguments and return the parsed arguments. If the arguments have already been parsed,
        return the cached parsed arguments.

        Returns:
            Namespace:
                The parsed arguments.
        """
        if self.__parsed is None:
            # Parse the command line arguments only once
            self.__parsed = self.parser.parse_args()
        return self.__parsed

    @classmethod
    def from_env(cls):
        """
        Create an instance of the class using environment variables.

        This method is useful when you want to create an instance of the class using environment variables.

        Returns:
            Arguments:
                An instance of the class with the host and port values set from the environment variables.
                If the environment variables are not set, the default values will be used.

        Example Usage:
            >>> from nepyc.server.cli.arguments import Arguments
            >>> args = Arguments.from_env()
            >>> print(args.parsed.host)
            'localhost'
            >>> print(args.parsed.port)
            8580

        """
        # Create an instance of the class
        instance = cls()

        # Override default values with those from environment variables if they exist
        env_host      = environ.get('NEPYC_BIND_HOST')
        env_port      = environ.get('NEPYC_BIND_PORT')
        env_log_level = environ.get('NEPYC_LOG_LEVEL')

        # Set the default values from the environment variables if they exist
        if env_host is not None:
            instance.parser.set_defaults(host=env_host)
        if env_port is not None:
            instance.parser.set_defaults(port=int(env_port))
        return instance
