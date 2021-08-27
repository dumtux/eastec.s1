from rich.panel import Panel
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Footer, Placeholder

import serial
import RPi.GPIO as GPIO


UART_EN = 12
UART_PORT = '/dev/serial0'

# enable UART level shifter on RJ45 connector
GPIO.setmode(GPIO.BCM)
GPIO.setup(UART_EN, GPIO.OUT)
GPIO.output(UART_EN, GPIO.HIGH)

# create serial port instance
ser = serial.Serial(port='/dev/serial0', baudrate=9600, timeout=1)


class Message:
    def __init__(self, desc: str, code: str):
        self.desc = desc
        self.code = code

    def get_code_in_bytes(self) -> bytes:
        return bytes(bytearray.fromhex(self.code))


message_dict = {
        'INIT':       Message('Initial Power On',     'CC 01 02 0B 0B 1E 56 00 00 00 64 64 64 D1 42 72'),
        'HEATER_ON':  Message('Power On to Heaters',  'CC 09 02 0B 0B 1E 56 00 00 00 64 64 64 01 42 7A'),
        'HEATER_OFF': Message('Power Off to Heater',  'CC 11 02 0B 0B 1E 55 00 00 00 64 64 64 01 C2 02'),
        'INC_TEMP':   Message('Increase Temperature', 'CC 01 02 0B 0B 1F 57 01 00 00 64 64 64 01 42 75'),
        'DEC_TEMP':   Message('Decrease Temperature', 'CC 01 02 0B 0B 1E 56 01 00 00 64 64 64 01 42 73'),
}


class Tick(Widget):

    mouse_over = Reactive(False)

    def __init__(self, msg: Message):
        super().__init__()
        self.msg = msg

    def render(self) -> Panel:
        return Panel(
                '[b]%s[/b] (%s)' % (self.msg.code, self.msg.desc),
                style=('on blue' if self.mouse_over else ''))

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    async def on_click(self, event: events.Click) -> None:
        await super().on_click(event)
        ser.write(self.msg.get_code_in_bytes())


class SOneApp(App):

    async def on_load(self, event: events.Load) -> None:
        # await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")


    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(Footer(), edge='bottom')
        # await self.view.dock(Placeholder(), edge='left', size=40)
        ticks = (Tick(msg) for k, msg in message_dict.items())
        await self.view.dock(*ticks, edge='top')


SOneApp.run()
GPIO.cleanup()
