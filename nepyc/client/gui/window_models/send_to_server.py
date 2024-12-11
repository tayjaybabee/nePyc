import PySimpleGUI as psg
from nepyc.client.gui.assets.status_led import ON as ON_LED, OFF as OFF_LED, NO_STATUS as NO_STATUS_LED
from nepyc.client.gui.assets.led_indicator import LEDIndicator, set_led_color
from nepyc.client.client import ImageClient



def window_layout():
    from nepyc.client.config import Config

    config = Config(skip_cli_args=True)
    host   = config.host
    port   = config.port

    if config.config_file_loaded:
        cb_checked = True
    else:
        cb_checked = False

    return [
        [psg.Text('Host:'), psg.InputText(host, key='TXI_HOST')],
        [psg.Text('Port:'), psg.InputText(port, key='TXI_PORT')],
        [psg.Checkbox('Save these settings', default=cb_checked, key='CB_SAVE')],
        [
            psg.Button('Test Connection', key='BTN_TEST', visible=False),
            LEDIndicator('LED_STATUS'),
        ],
        [psg.Ok(key='BTN_OK'), psg.Cancel('BTN_CANCEL')]
    ]


def check_if_should_be_visible(window):
    if window['TXI_HOST'].get() and window['TXI_PORT'].get():
        window['BTN_TEST'].update(visible=True)
    else:
        window['BTN_TEST'].update(visible=False)

    return window


def update_status_led(window, status):
    if status:
        set_led_color(window, 'LED_STATUS', 'green')
    else:
        set_led_color(window, 'LED_STATUS', 'red')


class SendToServerWindow:
    def __init__(self):
        self.__title   = 'Send to nePyc Server'
        self.__window  = None
        self.__layout  = None
        self.__running = False

    @property
    def built(self) -> bool:
        return all([self.__window, self.__layout])

    @property
    def layout(self):
        return self.__layout

    @property
    def running(self) -> bool:
        """

        """
        return self.__running

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, new):
        if self.running:
            raise RuntimeError('Cannot change the title of a running window')

        self.__title = new

    @property
    def window(self):
        return self.__window

    def build(self):
        if self.built:
            return

        self.__layout = window_layout()
        self.__window = psg.Window(self.title, self.layout)

    def disallow_non_numeric(self, key, value):
        if not value.isdigit():
            self.window[key].update(value=value[:-1])

    def exit_cleanly(self):
        self.__running = False
        self.window.close()
#       self.__window = None

    def run(self):
        if not self.built:
            self.build()

        self.__running = True

        while self.running:
            event, values = self.window(timeout=100)

            check_if_should_be_visible(self.window)

            if event in (None, 'BTN_CANCEL'):
                self.exit_cleanly()
                break

            elif event == 'TXI_PORT':
                self.disallow_non_numeric('TXI_PORT', values['TXI_PORT'])

            elif event in ('TXI_HOST', 'TXI_PORT'):
                check_if_should_be_visible(self.window)

            elif event == 'BTN_OK':
                print('OK')
                if values['CB_SAVE']:
                    print('Save settings')

            elif event == 'BTN_TEST':
                self.test_client_connection(values['TXI_HOST'], int(values['TXI_PORT']))

    def test_client_connection(self, host, port):
        client = ImageClient(host, port)
        try:
            client.connect()
        except ConnectionRefusedError:
            status = False

        status = client.connected
        client.close()

        update_status_led(self.window, status)
