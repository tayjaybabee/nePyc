from contextlib import contextmanager

import sys
import os
from contextlib import contextmanager


@contextmanager
def suppress_exception():
    """Context manager to suppress exceptions."""
    try:
        yield
    except Exception as e:
        # Suppress the exception by preventing its output
        sys.stderr.write(f"Exception suppressed: {str(e)}\n")
        pass  # You could also log the error or handle it differently if needed


@contextmanager
def suppress_stdout():
    """Context manager to suppress stdout."""
    original_stdout = sys.stdout  # Save the original stdout
    sys.stdout = open(os.devnull, 'w')  # Redirect stdout to null
    try:
        yield
    finally:
        sys.stdout.close()  # Close the null device
        sys.stdout = original_stdout  # Restore the original stdout
