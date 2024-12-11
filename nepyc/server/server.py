from nepyc.proto.ack import DISPATCHER, REJECT_ACK_MAP, OKAck
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
    """
    The ImageServer class is the main server class for the nePyc server system. This class is responsible for handling
    all incoming connections and handling the server logic. This class is also responsible for saving images to the save
    directory and displaying the images in the GUI.

    Attributes:
        save_images (bool):
            If True, incoming images will be saved to the save directory.

        save_directory (str):
            The directory to save incoming images to.

        save_images (bool):
            If True, images received and saved from previous sessions will be displayed.

        host (str):
            The host to bind the server to.

        port (int):
            The port to bind the server to.

        gui (nepyc.server.gui.SlideshowGUI):
            The GUI object for the slideshow aspect of the nePyc server system.
    """
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
        """
        Initialize the ImageServer instance.

        This constructor sets up the ImageServer with the specified configuration,
        including network settings, image saving options, and GUI initialization.

        Parameters:
            host (str):
                The host to bind the server to. Optional, defaults to 'localhost'.

            port (int):
                The port to bind the server to. Optional, defaults to 8085.

            save_incoming_images (bool):
                If True, incoming images will be saved to the save directory. Optional, defaults to False.

            save_directory (str):
                The directory to save incoming images to. Optional, defaults to "USER_PICTURES\nepyc".

            display_saved_images (bool):
                If True, images received and saved from previous sessions will be displayed. Optional, defaults to False.

        Returns:
            None

        Raises:
            ValueError:
                If the server is already running.

            TypeError:
                If the host is not a string.

            ConnectionError:
                If the port is not free.

        """
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
        """
        Return the display saved images flag. This will return the flag that determines if saved images should be
        displayed.

        Returns:
            bool:
                The display saved images flag.
        """
        return self.__display_saved_images

    @property
    def exit_flag(self):
        """
        Return the exit flag. This will return the exit flag that determines if the server should exit.

        Returns:
            threading.Event:
                The exit flag.
        """
        return exit_flag

    @property
    def gui(self):
        """
        Return the GUI object for the slideshow aspect of the nePyc server system.

        Returns:
            nepyc.server.gui.SlideshowGUI:
                The GUI object for the slideshow aspect of the nePyc server system

        """
        return self.__gui

    @property
    def host(self):
        """
        Return the host for the server to bind to.

        Returns:
            str:
                The host for the server to bind to.
        """
        return self.__host

    @host.setter
    def host(self, new):
        """
        Set the host for the server to bind to. This will set the host that the server will bind to. If the server is
        already running, an error will be raised. If the host is not a string, an error will be raised.

        Parameters:
            new (str):
                The new host to bind to (must be accessible to clients).

        Returns:
            None
        """
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
        """
        Return the collected images.

        Returns:
            list[PIL.Image]:
                The images collected by the server.
        """
        with self.__lock:
            return self.__images

    @images.deleter
    def images(self):
        """
        Delete the images. This will remove all images from the server. This will not delete the actual image files from
        the save directory (if any). This will only remove the images from the current session/slideshow.

        Returns:
            None
        """
        self.__images = []

    @property
    def image_hashes(self):
        """
        Return the image hashes.

        This will return the image hashes collected by the server. This will return a dictionary where the keys are the
        hashes of the images and the values are the file numbers of the images. This will return an empty dictionary if
        no images have been received.

        Returns:
            dict:
                The image hashes collected by the server.
        """
        return self.__image_hashes

    @image_hashes.deleter
    def image_hashes(self):
        """
        Deletes the image hashes. This will remove all image hashes from the hash database.

        Returns:
            None
        """
        self.__image_hashes = {}

    @property
    def port(self):
        """
        Return the port that the server is bound to. This will return the port that the server is bound to. This is the
        port that clients will connect to.

        Returns:
            int:
                The port that the server is bound to.
        """
        return self.__port

    @port.setter
    def port(self, new):
        """
        Set the port for the server to bind to. This will set the port that clients will connect to. If the specified port
        is occupied by another process (or the server is already running), an error will be raised. If the specified port
        is not an integer, an error will be raised. If the server is running, an error will be raised.

        Parameters:
            new (int):
                The new port to bind the server to.

        Returns:
            None

        Raises:
            ValueError:
                If the server is already running.

            TypeError:
                If the port is not an integer.

            ConnectionError:
                If the port is not free.
        """
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
            raise ConnectionError(f'Port {new} is not free, server may not be able to bind to it.')

        self.__port = new
        log.debug(f'Port set to {self.port}')

    @property
    def running(self) -> bool:
        """
        Return the running flag. This will return the flag that determines if the server is running.

        - If the flag is set to True, the server is running.

        - If the flag is set to False, the server is not running.

        Returns:
            bool:
                The running flag.
        """
        return self.__running

    @running.setter
    def running(self, new) -> None:
        """
        Set the running flag. This will set the flag that determines if the server is running.

        Parameters:
            new:
                The new value of the running flag.

        Returns:
            None
        """
        if not isinstance(new, bool):
            raise TypeError('Running must be a boolean')

        self.__running = new

    @property
    def save_images(self) -> bool:
        """
        Return the save images flag. This will return the flag that determines if incoming images should be saved to the
        save directory. If the flag is set to True, the save directory will be created if it does not exist.

        - If the flag is set to False, the save directory will not be created if it does not exist, and incoming images
        will not be saved to storage.

        - If the flag is set to True, the save directory will be created if it does not exist, and incoming images will
        be saved to storage.

        Returns:
            bool:
                The save images flag.
        """
        return self.__save_images

    @save_images.setter
    def save_images(self, new) -> None:
        """
        Set the save images flag. This will set the flag that determines if incoming images should be saved to the save
        directory. If the flag is set to True, the save directory will be created if it does not exist. If the flag is
        set to False, the save directory will not be created if it does not exist. If the flag is set to False and the
        save directory does not exist, incoming images will not be saved.

        Parameters:
            new (bool):
                The new value of the save images flag.

        Returns:
            None
        """
        if not isinstance(new, bool):
            raise TypeError('The save images flag must be a boolean!')

        self.__save_images = new

    @property
    def server(self):
        """
        Return the server socket.

        Returns:
            socket.socket:
                The server socket.
        """
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
        """
        Bind the server to the specified host and port. If the server is already running, an error will be raised. If
        the host is not set, an error will be raised. If the port is not free, an error will be raised.

        Returns:
            socket.socket:
                The server socket.
        """
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

        # Check if the server socket is already initialized
        if self.__server:
            log.debug('Server socket already initialized, skipping bind.')
            return self.__server

        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.server.bind((self.host, self.port))
        except PermissionError as e:
            log.error(f'Error binding to {self.host}:{self.port}: {e}')
            self.stop()

        log.debug(f'Server bound to {self.host}:{self.port}')

        return self.server

    def listen(self):
        """
        Listen for incoming connections. This will listen for incoming connections and then handle them in a separate
        thread. This will continue to listen for incoming connections until the server is stopped. This will not return
        until the server is stopped...

        Returns:
            None
        """
        log = self.create_logger()

        self.server.listen()
        log.debug(f'Server listening on {self.host}:{self.port}')
        self.running = True

        try:
            while self.running:
                self.server.settimeout(30)

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
        """
        Handle a client connection. This will receive image data from the client and then process it. If the image data
        is valid, it will be added to the list of images. If the image data is a duplicate, a duplicate ACK message will
        be sent to the client. If the image data is invalid, an invalid ACK message will be sent to the client. If the
        image data is valid and the save images flag is set, the image will be saved to the save directory.

        Parameters:
            client (socket.socket):
                The client sopcket to send the ACK.

            addr:
                The address of the client.

        Returns:
            None
        """
        log = self.create_logger()
        log.debug(f'Handling client {addr}')

        with client:
            while True:
                size_data = self.receive_data(client)

                if not size_data:
                    break

                size = struct.unpack('!I', size_data)[0]

                image_data = self.receive_image_data(client, size)

                if not image_data:
                    break

                if image := self.process_image(image_data, client):
                    log.debug('Image added to list of images')
                    self.images.append(image)

                log.debug('Response sent to client.')

    def process_image(self, image_data, client):
        """
        Process the image data received from the client. This will load the image data into a PIL Image object and then
        check if the image is a duplicate. If the image is not a duplicate, it will save the image to the save directory
        and append the hash of the image to the hash database. If the image is a duplicate, it will send a duplicate ACK
        message to the client. If the image data is invalid, it will send an invalid ACK message to the client.

        Args:
            image_data (bytes):
                The image data received from the client.

            client (socket.socket):
                The client socket.

        Returns:
            PIL.Image:
                The image object if the image data is valid, otherwise None.
        """
        log = self.create_logger()
        log.debug('Processing image data...')

        try:
            image = Image.open(BytesIO(image_data))
            image.load()

            if check_hash(image, self.image_hashes):
                log.debug('Duplicate image received, ignoring...')
                send_ack(DISPATCHER.dispatch(REJECT_ACK_MAP['DUP']), client)

                return None

            if self.save_images:
                log.debug('Saving image...')
                self.save_image(image, client)

            ack = DISPATCHER.dispatch(OKAck)

            send_ack(ack, client)

            return image

        except (OSError, ValueError) as e:
            log.error(f'Invalid image data: {e}')

            ack = DISPATCHER.dispatch(REJECT_ACK_MAP['INV'])
            send_ack(ack, client)

    def receive_data(self, client):
        log = self.create_logger()

        try:
            size_data = client.recv(4)

            if not size_data:
                log.debug('No more data from client')
                return None

            log.debug(f'Received size data: {size_data}')
            return size_data

        except socket.timeout:
            log.error('Socket timeout occurred while receiving size data')
            return None
        except socket.error as e:
            log.error(f'Socket error occurred while receiving size data: {e}')
            return None
        except Exception as e:
            log.error(f'An unexpected error occurred while receiving size data: {e}')
            return None

    def receive_image_data(self, client, size):
        """
        Receive image data from the client. This will receive the image data in chunks and then return the full image data.

        Parameters:
            client (socket.socket):
                The client socket connection to receive the image data from.

            size (int):
                The size (in bytes) of the image data to receive.

        Returns:
            bytes:
                The full image data.
        """
        log = self.create_logger()

        data = b''
        try:
            while len(data) < size:
                packet = client.recv(min(size - len(data), 1024))

                if not packet:
                    log.debug('No more data from client')

                    return None

                data += packet
                log.debug(f'Received {len(packet)} bytes of image data, total received: {len(data)} bytes')

            log.debug(f'Image data received. Total size: {len(data)}')
            return data

        except socket.timeout:
            log.error('Socket timeout occurred while receiving image data')
            return None
        except socket.error as e:
            log.error(f'Socket error occurred while receiving image data: {e}')
            return None
        except Exception as e:
            log.error(f'An unexpected error occurred while receiving image data: {e}')
            return None

    def run_server(self):
        """
        Run the server. This will bind the server to the host and port, then listen for incoming connections.

        Returns:
            None
        """
        self.bind()
        self.listen()

    def save_image(self, image, client):
        """
        Save an image to the save directory. This will save the image to the save directory and then append the hash of it
        to the hash database.

        Parameters:
            image (PIL.Image):
                The image to save.

            client (socket.socket):
                The client socket connection to send ACK messages to.

        Returns:
            None
        """
        log = self.create_logger()
        log.debug('Loading hashes...')

        known_hashes, missing_numbers, max_number = load_hash_data(self.save_directory)

        img_hash = hashlib.md5(image.tobytes()).hexdigest()

        if img_hash not in known_hashes:
            log.debug('Image not in hash database, saving...')

            file_number, max_number = assign_number(missing_numbers, max_number)

            file_name = f'{file_number}.png'
            image.save(f'{self.save_directory}/{file_name}')
            log.debug(f'Image saved to {self.save_directory}/{file_name}')
            append_hash_to_file(self.save_directory, img_hash, file_number)

        else:
            log.debug('Image already in hash database, ignoring...')
            send_ack(DISPATCHER.dispatch(REJECT_ACK_MAP['DUP']), client)

    def start(self) -> None:
        """
        Start the server. This will start the server in a separate thread and then start the GUI in the main thread.

        Returns:
            None
        """
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
        """
        Stop the server and the GUI. This will close the server socket and then stop the GUI.

        Parameters:
            from_gui (bool):
                If True, the GUI will not be stopped.

        Returns:
            None
        """
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
