from nepyc.proto.ack import Ack
from nepyc.proto.ack.registrar import REGISTRAR
import socket
import struct


def deserialize_ack(data: bytes) -> Ack:
    """
    Deserialize an ACK message from bytes.

    Parameters:
        data (bytes):
            The bytes to deserialize.

    Returns:
        Ack:
            The deserialized ACK message.
    """
    code_len = struct.unpack('!B', data[:1])[0]
    code = data[1:1 + code_len]

    parent_code, child_code = parse_full_code(code)

    full_code = f'{parent_code}:{child_code}'.encode('utf-8')

    return REGISTRAR.get_ack(full_code)

def parse_full_code(full_code: bytes) -> tuple[str, str]:
    """
    Parse a full code into its parent and child codes.

    Parameters:
        full_code (bytes):
            The full code to parse.

    Returns:
        tuple[str, str]:
            A tuple containing the parent and child codes.

    Examples:
        >>> parse_full_code(b'OK')
        ('OK', '')
        >>> parse_full_code(b'REJ:DUP')
        ('REJ', 'DUP')
    """
    parts = full_code.decode('utf-8').split(':')
    parent_code = parts[0]
    child_code = parts[1] if len(parts) > 1 else ''

    return parent_code, child_code


def send_ack(ack: Ack, conn: socket.socket) -> None:
    """
    Send an ACK message to the client.

    Parameters:
        ack (Ack):
            The ACK message to send.

        conn (socket.socket):
            The socket connection to send the ACK message to.

    Returns:
        None
    """
    conn.sendall(serialize_ack(ack))


def serialize_ack(ack: 'Ack') -> bytes:
    """
    Serialize an ACK message to a byte string.

    Parameters:
        ack (Ack):
            The ACK message to serialize.

    Returns:
        bytes:
            The serialized ACK message as a byte string.

    Examples:
        >>> serialize_ack(Ack())
        b'\x01\x00\x00\x00\x00\x00\x00\x00'
    """
    return ack.to_bytes()
