import queue
from tkinter import Tk, Label
from PIL import ImageTk, Image
import random
from nepyc.log_engine import ROOT_LOGGER, Loggable
from nepyc.server.signals import exit_flag


MOD_LOGGER = ROOT_LOGGER.get_child('server.gui')


class SlideshowGUI(Loggable):

    def __init__(self, server, width=800, height=600):
        super().__init__(MOD_LOGGER)
        self.__width = width
        self.__height = height

        self.__server = None
        self.__queue = queue.Queue()

        self.__root        = None
        self.__image_label = None

        self.__server = server

    def build(self):
        log = self.create_logger()
        log.debug('Building GUI')

        self.root.title('Slideshow')
        self.root.protocol('WM_DELETE_WINDOW', self.on_exit)
        self.image_label.pack()

    @property
    def exit_flag(self):
        return exit_flag

    @property
    def height(self):
        return self.__height

    @property
    def image_label(self):
        if not self.__image_label:
            self.__image_label = Label(self.root)

        return self.__image_label

    @property
    def queue(self):
        return self.__queue

    @property
    def root(self):
        if not self.__root:
            self.__root = Tk()

        return self.__root

    @property
    def server(self):
        if hasattr(self, 'class_logger'):
            log = self.create_logger()
        else:
            log = MOD_LOGGER.get_child('SlideshowGUI:server')

        if not self.__server:
            log.error('Server instance is not set!')

        return self.__server

    @property
    def width(self):
        return self.__width

    def check_exit(self):
        if exit_flag.is_set():
            self.on_exit()

        else:
            self.root.after(100, self.check_exit)

    def on_exit(self):
        log = self.create_logger()
        log.debug('Exiting GUI and stopping server...')

        if self.server:
            log.debug('Stopping server')
            self.server.stop(from_gui=True)

        if self.root:
            self.root.after_cancel(self.run)
            self.root.after_cancel(self.check_exit)
            self.root.destroy()

        log.debug('GUI exit scheduled!')

    def process_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()

                if message == 'EXIT':
                    self.server.stop()
        except queue.Empty:
            pass

        self.root.after(100, self.process_queue)


    def resize_image(self, img, target_width, target_height):
        original_width, original_height = img.size
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        resized_image = img.resize((new_width, new_height), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
        return resized_image

    def run(self):
        log = self.create_logger()

        if not self.root:
            log.error('Cannot start GUI loop; root window is not initialized!')
            return

        try:
            if self.exit_flag.is_set():
                self.on_exit()
                return

            self.update_image()
            self.root.after(2000, self.run)
        except Exception as e:
            log.error(f'Error running GUI loop: {e}')

    def start(self):
        log = self.create_logger()
        log.debug('Starting GUI')

        if not self.server or not self.server.running:
            if self.server:
                server.start()
            log.error('Server must be running to start GUI.')
            return

        self.build()

        try:
            self.run()
            self.root.after(100, self.process_queue())
        except KeyboardInterrupt:
            log.info('Exiting due to keyboard interrupt')

        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            log.info('Exiting due to keyboard interrupt')
        finally:
            self.on_exit()


    def stop(self):
        self.root.quit()

    def update_image(self):
        log = self.create_logger()

        if not self.root:
            log.error('Cannot update image; root window is not initialized!')
            return

        if self.server.images:
            try:
                img = random.choice(self.server.images)
                img = self.resize_image(img, self.width, self.height)
                pic = ImageTk.PhotoImage(img)
                self.image_label.config(image=pic)
                self.image_label.image = pic
            except Exception as e:
                self.create_logger().error(f'Error updating image: {e}')

        else:
            log.warning('No images to display!')
            self.image_label.config(image=None)
