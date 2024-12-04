from nepyc.common.utils import is_port_free
from nepyc.server.config import CONFIG
from nepyc.log_engine import ROOT_LOGGER, Loggable
from nepyc.server.gui import SlideshowGUI
import socket
import threading
from PIL import Image
from io import BytesIO
import struct
from nepyc.server.signals import exit_flag


MOD_LOGGER = ROOT_LOGGER.get_child('server.server')


class ImageServer(Loggable):
    DEFAULT_BIND_HOST = CONFIG.BIND_HOST
    DEFAULT_BIND_PORT = CONFIG.BIND_PORT

    def __init__(self, host=DEFAULT_BIND_HOST, port=DEFAULT_BIND_PORT):
        super().__init__(MOD_LOGGER)

        self.__host    = None
        self.__lock = threading.Lock()
        self.__port    = None
        self.__running = False
        self.__server  = None
        self.__images  = []

        self.host = host
        self.port = port
        self.__gui = SlideshowGUI(self)

    @property
    def exit_flag(self):
        return exit_flag

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
        with self.__lock:
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

        if not is_port_free(new, self.host):
            log.warning(f'Port {new} is not free, server may not be able to bind to it.')

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

    @property
    def size_of_images(self):
        """
        Return the total size (in bytes) of all received images.

        Returns:
            int:
                The total size of all images in bytes.
        """
        total_size = 0
        for image in self.images:
            with BytesIO() as img_buffer:
                image.save(img_buffer, format=image.format)
                total_size += len(img_buffer.getvalue())

        return total_size

    def bind(self):
        log = self.create_logger()
        log.debug(f'Binding server to {self.host}:{self.port}')

        if self.server:
            log.error('Server is already running, cannot bind again')
            raise ValueError('Server is already running')

        if not self.host:
            log.error('Host must be set before binding')
            raise ValueError('Host must be set before binding')

        if not is_port_free(self.port, self.host):
            log.error(f'Port {self.port} is not free, cannot bind to it')
            raise ValueError(f'Port {self.port} is not free, cannot bind to it')

        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server.bind((self.host, self.port))
        except PermissionError as e:
            log.error(f'Error binding to {self.host}:{self.port}: {e}')
            self.stop()

        log.debug(f'Server bound to {self.host}:{self.port}')

        return self.server

    def listen(self):
        log = self.create_logger()

        self.server.listen()
        log.debug(f'Server listening on {self.host}:{self.port}')
        self.running = True

        try:
            while self.running:
                self.server.settimeout(1.0)

                try:
                    conn, addr = self.server.accept()
                    log.debug(f'Accepted connection from {addr}')
                    threading.Thread(target=self.handle_client, args=(conn, addr)).start()

                except socket.timeout:
                    continue

                except OSError:
                    log.error('Error accepting connection')
                    break  # Break out of the loop, socket's been closed.

                log.debug(f'Connection from {addr}')

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

    def run_server(self):
        self.bind()
        self.listen()

    def start(self):
        log = self.create_logger()
        log.debug('Starting server')

        if self.running:
            log.error('Server is already running')
            raise ValueError('Server is already running')

        self.__running = True

        server_thread = threading.Thread(target=self.run_server, daemon=True)
        log.debug(f'Starting server thread {server_thread}')
        server_thread.start()

        try:
            # Start the GUI in the main
            self.gui.start()
        except KeyboardInterrupt:
            self.stop()
            print('Server and GUI have been stopped.')
            sys.exit(0)


        server_thread.join()


    def stop(self, from_gui=False):
        log = self.create_logger()
        log.debug('Stopping server...')

        self.running = False

        if self.server:
            try:
                self.server.close()
            except Exception as e:
                log.error(f'Error stopping server: {e}')

        log.debug('Server stopped.')
        if not from_gui:
            self.gui.queue.put('EXIT')
            self.gui.on_exit()

        log.debug('GUI stopped...')
