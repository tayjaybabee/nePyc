from nepyc.log_engine import ROOT_LOGGER, Loggable
from nepyc.client.config import CONFIG
import socket
from PIL import Image
from io import BytesIO
import struct

MOD_LOGGER = ROOT_LOGGER.get_child('client.client')


class ImageClient(Loggable):
    DEFAULT_SERVER_HOST = CONFIG.BIND_HOST
    DEFAULT_SERVER_PORT = CONFIG.BIND_PORT

    def __init__(self, host=DEFAULT_SERVER_HOST, port=DEFAULT_SERVER_PORT):
        super().__init__(MOD_LOGGER)

        self.__client = None

        self.__host   = None
        self.__port   = None

        self.host     = host
        self.port     = port

    @property
    def client(self):
        return self.__client

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
        except ConnectionRefusedError:
            log.error('Connection refused')
            raise ConnectionRefusedError('Connection refused')

        log.debug('Connected to server')

    def close(self):
        log = self.create_logger()
        log.debug('Closing connection to server')

        if not self.client:
            log.error('Client is not connected')
            raise ConnectionError('Client is not connected')

        self.client.close()
        self.__client = None

        log.debug('Connection closed')

    def send_image(self, image_path):
        log = self.create_logger()
        log.debug(f'Sending image at {image_path}')

        if not self.client:
            log.error('Client is not connected')
            raise ConnectionError('Client is not connected')

        with Image.open(image_path) as img:
            byte_arr = BytesIO()
            img.save(byte_arr, format='PNG')
            img_data = byte_arr.getvalue()

            size = struct.pack('!I', len(img_data))

            self.client.sendall(size + img_data)

        log.debug('Image sent')

        response = self.client.recv(1024)
        log.debug(f'Received response {response}')
