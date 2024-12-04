import socket


def is_port_free(port, host='127.0.0.1'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        try:
            sock.connect((host, port))
            return False

        except (socket.timeout, ConnectionRefusedError):
            return True
