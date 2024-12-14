from nepyc.client.log_engine import CLIENT_LOGGER as ROOT_LOGGER, Loggable
from nepyc.client.config import Config
from nepyc.proto.ack import RECEIVER
import socket
from PIL import Image
from io import BytesIO
import struct
from pathlib import Path


MOD_LOGGER = ROOT_LOGGER.get_child('client.client')

CONFIG = Config(skip_cli_args=True)


class ImageClient(Loggable):
    DEFAULT_SERVER_HOST = CONFIG.host
    DEFAULT_SERVER_PORT = CONFIG.port

    def __init__(self, host=DEFAULT_SERVER_HOST, port=DEFAULT_SERVER_PORT):
        super().__init__(MOD_LOGGER)
        self.__connected = False

        self.__client = None

        self.__host   = None
        self.__port   = None

        self.host     = host
        self.port     = port

    @property
    def client(self):
        return self.__client

    @property
    def connected(self):
        return self.__connected

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, new):
        log = self.create_logger()
        log.debug(f'Setting host to {new}')

        if self.client:
            log.error('Cannot change host while client is connected')
            raise ValueError('Cannot change host while client is connected')

        if not isinstance(new, str):
            log.error('Host must be a string')
            raise TypeError('Host must be a string')

        log.debug(f'Host set to {new}')

        self.__host = new

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, new):
        log = self.create_logger()
        log.debug(f'Setting port to {new}')

        if self.client:
            log.error('Cannot change port while client is connected')
            raise ValueError('Cannot change port while client is connected')

        if not isinstance(new, int):
            log.error('Port must be an integer')
            raise TypeError('Port must be an integer')

        log.debug(f'Port set to {new}')

        self.__port = new

    def connect(self):
        log = self.create_logger()
        log.debug('Connecting to server')

        if self.client:
            log.error('Client is already connected')
            raise ConnectionError('Client is already connected')

        if not self.host or not self.port:
            log.error('Host and port must be set before connecting')
            raise ConnectionError('Host and port must be set before connecting')

        try:
            self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
        except ConnectionRefusedError as e:
            log.error('Connection refused')
            raise ConnectionRefusedError('Connection refused') from e

        self.__connected = True
        self.client.settimeout(10)

        log.debug('Connected to server')

    def close(self):
        log = self.create_logger()
        log.debug('Closing connection to server')

        if not self.client:
            log.error('Client is not connected')
            raise ConnectionError('Client is not connected')

        try:
            self.client.close()
        except Exception as e:
            log.error(f'Error closing the connection: {e}')
            raise e
        self.__client = None

        log.debug('Connection closed')

    def send_image(self, image_path):
        log = self.create_logger()
        image_path = Path(image_path)
        log.debug(f'Sending image at "{image_path}"')

        if not self.client:
            log.error('Client is not connected')
            raise ConnectionError('Client is not connected')

        try:
            with Image.open(image_path) as img:
                byte_arr = BytesIO()
                img.save(byte_arr, format='PNG')
                img_data = byte_arr.getvalue()

                size = struct.pack('!I', len(img_data))

                self.client.sendall(size + img_data)

            log.debug('Image sent')

            response = self.receive_response()
            log.debug(f'Received response {response}')
        except Exception as e:
            log.error(f'Failed to send image: {e}')
            raise

        log.info(f'Sent image at "{image_path}" and received response {response.status}')

    def receive_response(self):
        from nepyc.proto.ack import Ack, ACK_MAP
        log = self.create_logger()
        response = b''

        while True:
            log.debug('Receiving response')
            part = self.client.recv(1024)
            response += part

            if len(part) < 1024:
                break

        log.debug('Response received')
        response = RECEIVER.receive(response)

        if not isinstance(response, Ack) and not issubclass(response.__class__, Ack):
            log.error('Received response is not an Ack instance')
            print(response)

        if response.status not in [b'OK', 'OK']:
            log.warning(f'Received response status is not OK: {response}')

        log.debug(f'Response: {response}')

        return response
