from nepyc.server.protocol.ack import ACK_MAP, ack_protocol


def ack_lookup(code: int):
    """
    Lookup the ACK message for a given code.


    Parameters:
        code (int):
            The ACK code to lookup.

    Returns:
        Ack:
            The ACK message for the given code.
    """
    return ACK_MAP.get(code, 'Unknown ACK code')


def serialize_ack(ack):
    """
    Serialize an ACK message to a byte string.

    Parameters:
        ack (Ack):
            The ACK message to serialize.

    Returns:
        bytes:
            The serialized ACK message as a byte string.
    """
    return ack.SerializeToString()


def send_ack(ack, conn):
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


def status_lookup(status, ack_map=ACK_MAP):
    """
    Lookup the ACK that corresponds to a status code ('OK', 'ERROR', etc).

    Parameters:
        status (str):
            The status code to lookup.

    Returns:
        Ack:
            The ACK message for the given status code.
    """
    for code, ack in ack_map.items():
        # Check if the current Ack has the matching status
        if ack.status == status:
            return ack

        # If there are children, check if any child has a matching status
        if ack.children:
            for child_code, child_ack in ack.children.items():
                # Check if the child status matches the given status
                if child_ack.status == status:
                    return child_ack

                # Construct a combined status like 'REJECT:INVALID' and check if it matches the given status
                combined_status = f"{ack.status}:{child_ack.status}"
                if combined_status == status:
                    return child_ack

                # Recursively search in the children
                result = status_lookup(status, {child_code: child_ack})
                if result:
                    return result

    return None


def deserialize_ack(data):
    """
    Deserialize an ACK message from a byte string.

    Parameters:
        data (bytes):
            The byte string to deserialize.

    Returns:
        Ack:
            The deserialized ACK message.
    """
    ack = ack_protocol.Ack()
    ack.ParseFromString(data)
    return ack


__all__ = [
    'ack_lookup',
    'deserialize_ack',
    'send_ack',
    'serialize_ack'
]
