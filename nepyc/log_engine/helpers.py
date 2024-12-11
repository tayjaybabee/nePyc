from contextlib import contextmanager

from jedi.inference.gradual.typeshed import try_to_load_stub_cached


@contextmanager
def suppress_log_output(target_logger):
    """
    A context manager that suppresses log output for all levels.

    Returns:
        None:
            No return value.
    """
    current_level = target_logger.console_level

    target_logger.set_level(console_level='critical')

    try:
        yield
    finally:
        target_logger.set_level(console_level=current_level)
