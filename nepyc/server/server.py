from nepyc.server.config import CONFIG
from nepyc.log_engine import ROOT_LOGGER, Loggable
from nepyc.server.gui import SlideshowGUI
import socket
import threading
from PIL import Image
from io import BytesIO
import struct


MOD_LOGGER = ROOT_LOGGER.get_child('server.server')


class ImageServer(Loggable):
    DEFAULT_BIND_HOST = CONFIG.BIND_HOST
    DEFAULT_BIND_PORT = CONFIG.BIND_PORT

    def __init__(self, host=DEFAULT_BIND_HOST, port=DEFAULT_BIND_PORT):
        super().__init__(MOD_LOGGER)

        self.__host    = None
        self.__port    = None
        self.__running = False
        self.__server  = None
        self.__images  = []

        self.host = host
        self.port = port
        self.__gui = SlideshowGUI(self)

    @property
    def gui(self):
        return self.__gui

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, new):
        log = self.create_logger()
        log.debug(f'Setting host to {new}')

        if self.server:
            log.error('Cannot change host while server is running')
            raise ValueError('Cannot change host while server is running')

        if not isinstance(new, str):
            log.error('Host must be a string')
            raise TypeError('Host must be a string')

        log.debug(f'Host set to {new}')

        self.__host = new

    @property
    def images(self):
        return self.__images

    @images.deleter
    def images(self):
        self.__images = []

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, new):
        log = self.create_logger()
        log.debug(f'Setting port to {new}')
        if self.server:
            log.error('Cannot change port while server is running')
            raise ValueError('Cannot change port while server is running')

        if not isinstance(new, int):
            log.error('Port must be an integer')
            raise TypeError('Port must be an integer')

        self.__port = new
        log.debug(f'Port set to {self.port}')

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, new):
        if not isinstance(new, bool):
            raise TypeError('Running must be a boolean')

        self.__running = new

    @property
    def server(self):
        return self.__server

    def bind(self):
        log = self.create_logger()
        log.debug(f'Binding server to {self.host}:{self.port}')

        if self.server:
            log.error('Server is already running, cannot bind again')
            raise ValueError('Server is already running')

        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))

        log.debug(f'Server bound to {self.host}:{self.port}')

        return self.server

    def listen(self):
        log = self.create_logger()

        self.server.listen()
        log.debug(f'Server listening on {self.host}:{self.port}')
        self.running = True

        try:
            while self.running:
                conn, addr = self.server.accept()
                log.debug(f'Connection from {addr}')

                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
        except KeyboardInterrupt:
            log.debug('Keyboard interrupt received, stopping server')
            self.running = False
        finally:
            self.server.close()

    def handle_client(self, client, addr):
        log = self.create_logger()
        log.debug(f'Handling client {client}')

        with client:
            while True:
                size_data = client.recv(4)
                if not size_data:
                    log.debug('No more data from client')
                    break

                size = struct.unpack('!I', size_data)[0]

                data = b''

                while len(data) < size:
                    packet = client.recv(min(size - len(data), 1024))

                    if not packet:
                        log.debug('No more data from client')
                        return

                    data += packet

                try:
                    image = Image.open(BytesIO(data))
                    image.verify()
                    image = Image.open(BytesIO(data))
                except (OSError, ValueError) as e:
                    log.error(f'Invalid image data: {e}')
                    client.sendall(b'Image data invalid')
                    continue
                    # This forces the complete loading of the image
                self.images.append(image)
                log.debug('Image added to list')
                client.sendall(b'OK')
                log.debug('Response sent')

    def start(self):
        log = self.create_logger()
        log.debug('Starting server')

        if self.running:
            log.error('Server is already running')
            raise ValueError('Server is already running')

        gui_thread = threading.Thread(target=self.gui.start, daemon=True)
        gui_thread.start()

        self.bind()
        self.listen()

        log.debug('Server started')
