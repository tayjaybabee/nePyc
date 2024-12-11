from nepyc.proto.ack.models.base import Ack


class RejectAck(Ack):
    PARENT_CODE = b'REJ'
    CHILD_CODE = b'REJ'
    DESCRIPTION = b'Image data received and rejected.'
    status = 'ERROR'


# class RejectAck(Ack):
#     PARENT_CODE = b'REJ'
#     STATUS = b'REJECT'
#     DESCRIPTION = b'REJECT - The image data was rejected.'
#     _child_registry = {}
#
#     @classmethod
#     def register_child(cls, child_code: bytes, child_class: type):
#         print(f'Registering child {child_class} with code {child_code}')
#         cls._child_registry[child_code] = child_class
#
#     @property
#     def child_description(self) -> bytes:
#         return self.CHILD_DESCRIPTION if hasattr(self, 'CHILD_DESCRIPTION') else b''
#
#     @property
#     def size(self) -> int:
#         return len(self.full_code)
#
#     def to_bytes(self) -> bytes:
#         return struct.pack('!I', self.size) + self.full_code
#
#
#     @classmethod
#     def from_bytes(cls, data: bytes) -> 'RejectAck':
#         if len(data) < 4:
#             raise ValueError('Data too short for Reject ack')
#
#         size = struct.unpack('!I', data[:4])[0]
#         code_data = data[4:4 + size]
#
#         # code_data should be like b'REJ:DUP'
#         parts = code_data.split(b':', 1)
#         if len(parts) != 2:
#             raise ValueError('Invalid reject code format. Expected "REJ:CHILD".')
#
#         parent_code, child_code = parts
#
#         if parent_code != cls.PARENT_CODE:
#             raise ValueError('Not a Reject code')
#
#         if child_code not in cls._child_registry:
#             raise ValueError(f'Unknown child code for REJECT: {child_code}')
#
#         child_class = cls._child_registry[child_code]
#         return child_class()
#
#
#     @classmethod
#     def _from_child(cls, child_code: bytes) -> 'RejectAck':
#         # This method can be used if you need an alternate path for reconstruction.
#         # Not strictly needed since we handle it directly in from_bytes().
#         if child_code not in cls._child_registry:
#             raise ValueError(f'No registered class for child code: {child_code}')
#         return cls._child_registry[child_code]()
