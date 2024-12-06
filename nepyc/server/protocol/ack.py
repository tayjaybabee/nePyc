from nepyc.proto import ack_protocol

ACK_MAP = {
    0x00: ack_protocol.Ack(code=0x00, status='OK', description='The request was successful.'),
    0x01: ack_protocol.Ack(code=0x01, status='REJECT', description='The request was rejected.', children={
        0x01a: ack_protocol.Ack(code=0x01a, status='DUPLICATE', description='Indicates that the request was a duplicate.'),
        0x01b: ack_protocol.Ack(code=0x01b, status='INVALID', description='Indicates that the request was invalid.'),
        0x01c: ack_protocol.Ack(code=0x01c, status='ERROR', description='Indicates that an error occurred.'),
        0x01d: ack_protocol.Ack(code=0x01d, status='NO_MORE_DATA',
                           description='Indicates that no more data is available to process.'),
    0x0404: ack_protocol.Ack(code=0x1404, status='NOT_FOUND', description='Indicates that the ACK code was not found.'),
    })
}
