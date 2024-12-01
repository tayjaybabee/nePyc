from tkinter import Tk, Label
from PIL import ImageTk, Image
import random
from nepyc.log_engine import ROOT_LOGGER, Loggable


MOD_LOGGER = ROOT_LOGGER.get_child('server.gui')


class SlideshowGUI(Loggable):

    def __init__(self, server, width=800, height=600):
        super().__init__(MOD_LOGGER)
        self.__width = width
        self.__height = height

        self.__server = None

        self.__root        = None
        self.__image_label = None

        self.__server = server

    def build(self):
        log = self.create_logger()
        log.debug('Building GUI')

        self.root.title('Slideshow')
        self.image_label.pack()

    @property
    def height(self):
        return self.__height

    @property
    def image_label(self):
        if not self.__image_label:
            self.__image_label = Label(self.root)

        return self.__image_label

    @property
    def root(self):
        if not self.__root:
            self.__root = Tk()

        return self.__root

    @property
    def server(self):
        return self.__server

    @property
    def width(self):
        return self.__width


    def resize_image(self, img, target_width, target_height):
        original_width, original_height = img.size
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        resized_image = img.resize((new_width, new_height), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
        return resized_image

    def run(self):
        self.update_image()
        self.root.after(2000, self.run)

    def start(self):
        self.build()
        self.run()
        self.root.mainloop()

    def update_image(self):
        if self.server.images:
            try:
                if self.server.images:
                    img = random.choice(self.server.images)
                    img = self.resize_image(img, self.width, self.height)
                    pic = ImageTk.PhotoImage(img)
                    self.image_label.config(image=pic)
                    self.image_label.image = pic
            except Exception as e:
                self.create_logger().error(f'Error updating image: {e}')
