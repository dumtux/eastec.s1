from rich.panel import Panel
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget
from textual.widgets import Footer, Placeholder

import serial
import RPi.GPIO as GPIO


class Status:
    HEATER_VALS = {0: 0, 1: 30, 2: 50, 3: 70, 4: 100}

    def __init__(self):
        self.heater = False  # on/off, determined by set temperature vs read temperature, set time vs ellapsed time
        self.pwr = False     # on/off
        self.lac = False     # on/off
        self.l1_mode = 0     # 0 - 8
        self.l2 = False      # on/off
        self.temp = 0        # temperature 20 - 70
        self.time = 0        # minutes 0 - 90
        self.auto_hh = 0     # automode hour 0 - 23
        self.auto_mm = 0     # automode minute 0 - 59
        self.ht1 = 0         # heater 1 level 0 - 4, 0-0%, 1-30%, 2-50%, 3-75$, 4-100%
        self.ht2 = 0         # heater 2 level 0 - 4
        self.ht3 = 0         # heater 3 level 0 - 4

    def bytes(self) -> bytes:
        a = []
        a.append(0xcc)
        a.append((self.heater * 1 + self.lac * 2 + self.l2 * 4) * 0x10 + (1 if self.pwr else 9))
        a.append(self.time)
        a.append(self.auto_hh)
        a.append(self.auto_mm)
        a.append(self.temp)
        a.append(int(self.temp * 9 / 5) + 32)
        a.append(0)
        a.append(0)
        a.append(0)
        a.append(self.HEATER_VALS[self.ht1])
        a.append(self.HEATER_VALS[self.ht2])
        a.append(self.HEATER_VALS[self.ht3])
        a.append(self.l1_mode)
        a.append(0x42)
        a.append((sum(a) - 0xcc - 138) % 256)
        t = ' '.join([format(x, '02x') for x in a])
        print(t)
        ba = bytearray.fromhex(t)
        return bytes(ba)

    def update(self, code: str):
        if code == 'PWR':
            self.pwr = not self.pwr
            self.heater = not self.heater
        elif code == 'LAC':
            self.lac = not self.lac
        elif code == 'L1':
            self.l1_mode = (self.l1_mode + 1) % 9
        elif code == 'L2':
            self.l2 = not self.l2
        elif code == 'TPP':
            self.temp += 1
            if self.temp > 70:
                self.temp = 20
        elif code == 'TPM':
            self.temp -= 1
            if self.temp < 20:
                self.temp = 70
        elif code == 'TMP':
            self.time += 1
            if self.time > 90:
                self.time = 0
        elif code == 'TMM':
            self.time -= 1
            if self.time < 0:
                self.time = 90
        elif code == 'HT1':
            self.ht1 -= 1
            if self.ht1 < 0:
                self.ht1 = 4
        elif code == 'HT2':
            self.ht2 -= 1
            if self.ht2 < 0:
                self.ht2 = 4
        elif code == 'HT3':
            self.ht3 -= 1
            if self.ht3 < 0:
                self.ht3 = 4
        else:
            raise Exception("unknown button code [%s]" % code)


class Button:
    def __init__(self, code: str, text: str):
        self.code = code
        self.text = text


UART_EN = 12
UART_PORT = '/dev/serial0'

# enable UART level shifter on RJ45 connector
GPIO.setmode(GPIO.BCM)
GPIO.setup(UART_EN, GPIO.OUT)
GPIO.output(UART_EN, GPIO.HIGH)

# create serial port instance
ser = serial.Serial(port='/dev/serial0', baudrate=4800, timeout=1)

status = Status()

buttons = [
    Button('PWR', "Power"),
    Button('LAC', "Light AC"),
    Button('L1', "Light 1"),
    Button('L2', "Light 2"),
    Button('TPP', "Temperature +"),
    Button('TPM', "Temperature -"),
    Button('TMP', "Time +"),
    Button('TMM', "Time -"),
    Button('HT1', "Heater 1"),
    Button('HT2', "Heater 2"),
    Button('HT3', "Heater 3"),
]


class ButtonTick(Widget):

    mouse_over = Reactive(False)

    def __init__(self, btn: Button):
        super().__init__()
        self.btn = btn

    def render(self) -> Panel:
        return Panel(
                self.btn.text,
                style=('on blue' if self.mouse_over else ''))

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False

    async def on_click(self, event: events.Click) -> None:
        await super().on_click(event)
        status.update(self.btn.code)
        ser.write(status.bytes())


class SOneApp(App):

    async def on_load(self, event: events.Load) -> None:
        # await self.bind("b", "view.toggle('sidebar')", "Toggle sidebar")
        await self.bind("q", "quit", "Quit")


    async def on_mount(self, event: events.Mount) -> None:
        await self.view.dock(Footer(), edge='bottom')
        # await self.view.dock(Placeholder(), edge='left', size=40)
        ticks = (ButtonTick(btn) for btn in buttons)
        await self.view.dock(*ticks, edge='top')


SOneApp.run()
GPIO.cleanup()


