
"""
This module contains the signal handler for SIGINT (Ctrl+C)

Example Usage:
    >>> from nepyc.server.signals import setup_signal_handler
    >>> setup_signal_handler()
    >>> import time
    >>> time.sleep(10)
    >>> exit_flag
    True
"""
import os
import sys
import signal
from threading import Event


exit_flag = Event()



def setup_signal_handler():
    """
    Setup the signal handler for SIGINT (Ctrl+C)

    Returns:
        None
    """
    def signal_handler(signum, frame):
        exit_flag.set()
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal_handler)


__all__ = [
    'exit_flag',
    'setup_signal_handler',
]
