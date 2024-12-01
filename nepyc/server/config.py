from os import environ
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    BIND_HOST: str = environ.get('NEPYC_BIND_HOST', '0.0.0.0')
    BIND_PORT: int = int(environ.get('NEPYC_BIND_PORT', 8085))
    LOG_LEVEL: str = environ.get('NEPYC_LOG_LEVEL', 'DEBUG')


CONFIG = Config()
