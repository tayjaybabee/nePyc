from nepyc.proto.ack.models.base import Ack


class OKAck(Ack):
    CHILD_CODE = b'OK'
    DESCRIPTION = b'Successful Operation'
    status = 'OK'
