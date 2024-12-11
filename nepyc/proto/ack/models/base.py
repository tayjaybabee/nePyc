import struct
import uuid


class Ack:
    """
    Base class for all ACK messages.
    """
    PARENT_CODE = b'ACK'
    status = 'UNKNOWN'

    def __init__(self):
        self.__uuid = uuid.uuid4().hex  # UUID for identifying the message
        self.children = {}

    @property
    def full_code(self) -> bytes:
        """
        The full ACK code, including any child code.
        Example: 'REJ:DUP' where 'REJ' is the parent and 'DUP' is the child.
        """
        return self.PARENT_CODE + (b':' + self.child_code() if self.child_code() else b'')

    def child_code(self) -> bytes:
        """Return the child part of the code if it exists."""
        return getattr(self, 'CHILD_CODE', b'')  # If no child, return an empty byte string

    @property
    def uuid(self) -> str:
        """Returns the UUID as a string (metadata only)."""
        return self.__uuid

    def to_bytes(self) -> bytes:
        """
        Convert the ACK object to bytes for serialization.
        Serializes only the full_code and child code, excluding UUID for serialization purposes.
        """
        full_code = self.full_code
        uuid_bytes = self.uuid.encode('utf-8')
        return (
            struct.pack('!B', len(full_code))
            + full_code
            + struct.pack('!B', len(uuid_bytes))
            + uuid_bytes
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Ack':
        """
        Deserialize an ACK from a byte string.
        Only the full_code will be used to identify the ACK.
        """
        from nepyc.proto.ack import REJECT_ACK_MAP, OKAck
        ack = None

        full_code_length = struct.unpack('!B', data[:1])[0]
        full_code = data[1:1 + full_code_length]
        parent_code, child_code = full_code.split(b':', 1) if b':' in full_code else (full_code, b'')
        if parent_code == b'REJ':
            if child_code in REJECT_ACK_MAP.keys():
                ack = REJECT_ACK_MAP[child_code]()
            else:
                raise ValueError(f'Unknown REJECT code: {child_code}')

        elif child_code == b'OK':
            ack = OKAck()

        if not ack:
            raise ValueError(f'Unknown ACK code: {full_code}')

        uuid_length = struct.unpack('!B', data[1 + full_code_length:2 + full_code_length])[0]
        uuid_str = data[2 + full_code_length:2 + full_code_length + uuid_length].decode('utf-8')

        ack.__uuid = uuid_str  # Assign UUID from the deserialized data

        return ack

    def register_child(self, child_code: bytes, child_ack: 'Ack'):
        """
        Register a child ACK under this parent ACK.
        
        Parameters:
            child_code (bytes): The code that identifies the child ACK.
            child_ack (Ack): The child ACK class to register.
        """
        self.children[child_code] = child_ack

    def __repr__(self):
        return f'<{self.__class__.__name__} {self.full_code.decode("utf-8")}> {self.status} (...{self.uuid[-6:]})'

    def __str__(self):
        desc_prefix = ' - '
        desc_str = f'{desc_prefix}{self.DESCRIPTION.decode("utf-8")}' if hasattr(self, 'DESCRIPTION') else ''

        return f'{self.status}{desc_str} ({self.full_code.decode("utf-8")})'
