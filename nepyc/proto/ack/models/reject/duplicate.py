from nepyc.proto.ack.models.reject.base import RejectAck


class DuplicateAck(RejectAck):
    CHILD_CODE = b'DUP'
    DESCRIPTION = b'Rejected due to the presence of duplicate image data'
    status = 'DUPLICATE'


# class DuplicateAck(RejectAck):
#
#     CHILD_DESCRIPTION: bytes = b'DUPLICATE - Rejected due to duplicate image data.'
#     CHILD_CODE:        bytes = b'DUP'
#
#     @classmethod
#     def from_bytes(cls, data: bytes) -> 'DuplicateAck':
#         return super().from_bytes(data)
#
#     @property
#     def child_description(self) -> bytes:
#         return self.CHILD_DESCRIPTION
#
#     @classproperty
#     def status(self):
#         return b'DUPLICATE'
