
from nepyc.proto.ack.models.reject.base import RejectAck
from nepyc.proto.ack.models.reject.invalid import InvalidAck
from nepyc.proto.ack.models.reject.duplicate import DuplicateAck

RejectAckMap = {
    b'DUP': DuplicateAck,
    b'INV': InvalidAck
}

REJECT_ACK_MAP = RejectAckMap


__all__ = [
    'RejectAck',
    'InvalidAck',
    'DuplicateAck'
]
