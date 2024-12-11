from nepyc.proto.ack.models.reject.base import RejectAck


class InvalidAck(RejectAck):
    CHILD_CODE = b'INV'
    DESCRIPTION = b'Invalid image data received.'
    status = 'INVALID'
