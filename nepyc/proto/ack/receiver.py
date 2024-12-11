from nepyc.proto.ack import Ack


class AckReceiver:
    """Singleton class responsible for receiving and processing acknowledgment messages."""

    _instance = None
    _received_acks = {}  # A store to keep track of received ACKs by UUID

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(AckReceiver, cls).__new__(cls)
        return cls._instance

    def receive(self, data: bytes):
        """
        Receive serialized data, deserialize it, and store the ACK message.
        """
        ack = Ack.from_bytes(data)
        self._received_acks[ack.uuid] = ack
        return ack

    def get_received_ack(self, uuid: str) -> Ack:
        """
        Retrieve a received ACK by its UUID.
        """
        return self._received_acks.get(uuid)


RECEIVER = AckReceiver()
