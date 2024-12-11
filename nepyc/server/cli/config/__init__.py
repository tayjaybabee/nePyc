from os import environ
from dataclasses import dataclass
from nepyc.common.config.dirs import DEFAULT_DIRS


DEFAULT_SAVE_IMAGE_DIR = DEFAULT_DIRS.user_pictures_path.joinpath('nepyc')


@dataclass(frozen=True)
class Config:
    BIND_HOST:               str  = environ.get('NEPYC_BIND_HOST', '0.0.0.0')
    BIND_PORT:               int  = int(environ.get('NEPYC_BIND_PORT', 8085))
    LOG_LEVEL:               str  = environ.get('NEPYC_LOG_LEVEL', 'DEBUG')
    SAVE_IMAGES:             bool = bool(environ.get('NEPYC_SAVE_IMAGES', False))
    SAVE_IMAGE_DIR:          str  = environ.get('NEPYC_SAVE_IMAGE_DIR', DEFAULT_SAVE_IMAGE_DIR)
    DO_DISPLAY_SAVED_IMAGES: bool = bool(environ.get('NEPYC_DISPLAY_SAVED', False))


ENV_CONFIG = Config()
