from pathlib import Path

from inspyre_toolbox.ver_man import PyPiVersionInfo, VersionParser
from inspyre_toolbox.ver_man.helpers import read_version_file
from inspyre_toolbox.ver_man.classes.pypi import load_pypi_version_info
from nepyc.common.utils.context_managers import suppress_stdout, suppress_exception


VERSION_FILE_NAME = 'VERSION'


def get_version_file_path(version_file_name: str = VERSION_FILE_NAME) -> Path:
    """
    Gets the version-file path.

    Parameters:
        version_file_name (str, optional):
            The name of the version file. Defaults to :str:'VERSION

    Returns:
        Path:
            The version-file path.

    Since:
        v1.6.0

    Example Usage:
        >>> from nepyc.common.about.version import get_version_file_path
        >>> file_path = get_version_file_path()
        >>> print(file_path)
        Path('path/to/version/file')
    """
    return Path(__file__).parent / version_file_name


VERSION_FILE_PATH = get_version_file_path()

VERSION = VersionParser(read_version_file(VERSION_FILE_PATH))

VERSION_NUMBER = VERSION.parse_version()

# Clean up the namespace
del get_version_file_path
del VersionParser
del VERSION_FILE_PATH
del read_version_file

with suppress_exception():
    with suppress_stdout():
        PYPI_VERSION_INFO = load_pypi_version_info('nepyc')

__all__ = [
    'VERSION',
    'VERSION_NUMBER',
    'PYPI_VERSION_INFO',
]
