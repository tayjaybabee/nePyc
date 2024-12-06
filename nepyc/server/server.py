from nepyc.common.utils import is_port_free
from nepyc.server.cli.config import ENV_CONFIG as CONFIG
from nepyc.log_engine import ROOT_LOGGER, Loggable
from nepyc.server.gui import SlideshowGUI
from nepyc.server.utils.hashes import check_hash, load_hash_data, append_hash_to_file
from nepyc.server.utils.images import assign_number, load_all_images
from nepyc.server.protocol import ack_lookup, send_ack, deserialize_ack, status_lookup
import socket
import threading
from PIL import Image
from io import BytesIO
import struct
from nepyc.server.signals import exit_flag
from pathlib import Path
import sys
import hashlib


MOD_LOGGER = ROOT_LOGGER.get_child('server.server')


class ImageServer(Loggable):
    DEFAULT_BIND_HOST = CONFIG.BIND_HOST
    DEFAULT_BIND_PORT = CONFIG.BIND_PORT
    DEFAULT_DO_SAVE   = CONFIG.SAVE_IMAGES
    DEFAULT_SAVE_DIR  = CONFIG.SAVE_IMAGE_DIR

    def __init__(
            self,
            host=DEFAULT_BIND_HOST,
            port=DEFAULT_BIND_PORT,
            save_incoming_images=False,
            save_directory=CONFIG.SAVE_IMAGE_DIR,
            display_saved_images=False
    ):
        super().__init__(MOD_LOGGER)
        log = self.class_logger
        self.__display_saved_images = display_saved_images

        self.__host        = None
        self.__lock        = threading.Lock()
        self.__port        = None
        self.__running     = False
        self.__save_images = False
        self.__server      = None
        self.__images      = []
        self.__image_hashes = {}

        self.save_images = save_incoming_images
        log.debug(f'Save images set to {self.save_images}')

        self.save_directory = save_directory
        log.debug(f'Save directory set to {self.save_directory}')

        self.__saved_image_hashes = {

        }

        self.host = host
        log.debug(f'Host set to {self.host}')

        self.port = port
        log.debug(f'Port set to {self.port}')

        self.__gui = SlideshowGUI(self)
        log.debug(f'GUI created: {self.gui}')

        if self.display_saved_images:
            self.__images.extend(load_all_images(self.save_directory))


        if self.save_images:
            target_dir = Path(self.save_directory)
            if not target_dir.exists():
                log.debug(f'Creating save directory {self.save_directory}')
                target_dir.mkdir(parents=True, exist_ok=True)

            else:
                if not target_dir.joinpath('.manifest').exists():
                    log.debug(f'Creating manifest file {target_dir.joinpath(".manifest")}')
                    target_dir.joinpath('.manifest').touch()

    @property
    def display_saved_images(self):
        return self.__display_saved_images

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
    def image_hashes(self):
        return self.__image_hashes

    @image_hashes.deleter
    def image_hashes(self):
        self.__image_hashes = {}

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
    def save_images(self):
        return self.__save_images

    @save_images.setter
    def save_images(self, new):
        if not isinstance(new, bool):
            raise TypeError('The save images flag must be a boolean!')

        self.__save_images = new

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
                    if not self.running:
                        break
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
                    image.load()

                    if check_hash(image, self.image_hashes):
                        log.debug('Duplicate image received, ignoring...')
                        send_ack(status_lookup('DUPLICATE'), client)

                        continue

                    if self.save_images:
                        print('Loading hashes...')
                        known_hashes, missing_numbers, max_number = load_hash_data(self.save_directory)
                        print(known_hashes, missing_numbers, max_number)
                        img_hash = hashlib.md5(image.tobytes()).hexdigest()

                        if not img_hash in known_hashes:
                            log.debug('Image not in hash database, saving...')
                            file_number, max_number = assign_number(missing_numbers, max_number)
                            file_name = f'{file_number}.png'
                            image.save(f'{self.save_directory}/{file_name}')
                            log.debug(f'Image saved to {self.save_directory}/{image.filename}')
                            append_hash_to_file(self.save_directory, img_hash, file_number)
                        else:
                            log.debug('Image already in hash database, ignoring...')
                            send_ack(status_lookup('DUPLICATE'), client)
                            continue

                    ack = status_lookup('OK')
                    send_ack(ack, client)


                except (OSError, ValueError) as e:
                    log.error(f'Invalid image data: {e}')
                    ack = status_lookup('INVALID')
                    send_ack(ack, client)
                    client.sendall(b'Image data invalid')
                    continue
                    # This forces the complete loading of the image
                self.images.append(image)
                log.debug('Image added to list')
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

        if self.save_images and not Path(self.save_directory).exists():
            log.debug(f'Creating save directory {self.save_directory}')
            Path(self.save_directory).mkdir(parents=True, exist_ok=True)

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
