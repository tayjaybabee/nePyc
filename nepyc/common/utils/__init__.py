from nepyc.common.utils.ports import is_port_free


def is_port_occupied(port, host=None):
    if host is None:
        host = 'localhost'
    return not is_port_free(port, host)



__all__ = [
    'is_port_free',
    'is_port_occupied'
]
