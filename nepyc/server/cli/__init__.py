from nepyc.server.cli.arguments import Arguments


ARGS = Arguments.from_env()


del Arguments


__all__ = [
    'ARGS',
]
