from nepyc.proto.ack import Ack


class AckDispatcher:
    """Singleton class responsible for dispatching acknowledgment messages."""

    _instance = None
    _ack_store = {}  # A store to keep track of dispatched ACKs by UUID

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(AckDispatcher, cls).__new__(cls)
        return cls._instance

    def dispatch(self, ack_type: Ack):
        """
        Create an ACK, assign a UUID, and store it in the dispatcher.
        """
        ack = ack_type()  # Create an instance of the ACK type
        self._ack_store[ack.uuid] = ack
        return ack

    def get_ack(self, uuid: str) -> Ack:
        """
        Retrieve an ACK by its UUID.
        """
        return self._ack_store.get(uuid)

    def serialize_ack(self, ack: Ack) -> bytes:
        """
        Serialize an ACK object to a byte string.
        """
        return ack.to_bytes()


DISPATCHER = AckDispatcher()
