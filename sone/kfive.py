import serial
from serial.serialutil import SerialException

from .utils import async_wrap
from .conf import UART_EN_PIN, UART_BAUDRATE, UART_PORT
from .models import Status
from .singletone import Singleton
from .utils import Logger, is_raspberry


logger = Logger.instance()


class KFive(Singleton):
    HEATER_VALS = {0: 0, 1: 30, 2: 50, 3: 70, 4: 100}

    uart: serial.Serial = None

    heater: bool  = False  # on/off, determined by target temperature vs read temperature, target time vs ellapsed time
    pwr: bool  = False     # on/off
    lac: bool  = False     # on/off
    l1_mode: int  = 0      # 0 - 8
    l2: bool  = False      # on/off
    target_temperature: int  = 0         # temperature 20 - 70
    read_temperature: int  = 0           # read temperature from box
    time: int  = 0         # minutes 0 - 90
    auto_hh: int  = 0      # automode hour 0 - 23
    auto_mm: int  = 0      # automode minute 0 - 59
    ht1: int  = 0          # heater 1 level 0 - 4, 0-0%, 1-30%, 2-50%, 3-75$, 4-100%
    ht2: int  = 0          # heater 2 level 0 - 4
    ht3: int  = 0          # heater 3 level 0 - 4
    endbyte: int = 0x42    # changes

    def to_bytes(self, set_time=False, set_temp=False) -> bytes:
        a = []
        a.append(0xcc)
        a.append((self.heater * 1 + self.lac * 2 + self.l2 * 4) * 0x10 + (1 if self.pwr else 9))
        a.append(self.time)
        a.append(self.auto_hh)
        a.append(self.auto_mm)
        a.append(self.target_temperature)
        a.append(int(self.target_temperature * 9 / 5) + 32)
        if set_time:
            a.append(2)
            a.append(0)
            a.append(1)
        elif set_temp:
            a.append(1)
            a.append(0)
            a.append(0)
        else:
            a.append(0)
            a.append(0)
            a.append(0)
        a.append(self.HEATER_VALS[self.ht1])
        a.append(self.HEATER_VALS[self.ht2])
        a.append(self.HEATER_VALS[self.ht3])
        a.append(self.l1_mode)
        a.append(self.endbyte)
        a.append((sum(a) - 0xcc - 138) % 256)
        t = ' '.join([format(x, '02x') for x in a])
        # print(t)
        ba = bytearray.fromhex(t)
        return bytes(ba)

    async def update(self, status: Status, set_time=False, set_temp=False) -> Status:
        if set_temp:
            self.target_temperature = status.target_temperature
        elif set_time:
            self.time = status.timer
        self.ht1 = status.heaters[0].level
        self.ht2 = status.heaters[1].level
        self.ht3 = status.heaters[2].level

        if self.time == 0:
            self.pwr = False
            self.heater = False
            self.endbyte = 0x42
            status.state = 'standby'
        else:
            if status.state == 'standby' or status.state == 'ready' or status.state == 'paused':
                self.pwr = False
                self.heater = False
                self.endbyte = 0x42
            elif status.state == 'heating' or status.state == 'insession':
                self.pwr = True
                self.heater = self.target_temperature > self.read_temperature
                self.endbyte = 0xC2 if self.heater else 0x02

        await self.write_uart(set_time=set_time, set_temp=set_temp)
        await self.read_uart()

        status.timer = self.time
        status.target_temperature = self.target_temperature
        status.current_temperature = self.read_temperature
        return status

    def init_uart(self):
        if not is_raspberry():
            logger.warn("Host OS is not a Raspberry, the SOne will be run in mocking mode.")
            return

        try:
            self.uart = serial.Serial(port=UART_PORT, baudrate=UART_BAUDRATE, timeout=1)
        except serial.serialutil.SerialException:
            self.uart = None
            logger.warn("Failed to open serial port. Serial port is not enabled on configuration, or used by other application.")

    @async_wrap
    def write_uart(self, set_time=False, set_temp=False):
        bytesdata = self.to_bytes(set_time=set_time, set_temp=set_temp)
        logger.log("SOne -> KFive: " + ' '.join([format(x, '02x') for x in bytesdata]))
        if self.uart is None:
            logger.warn("KFive.uart is not initialized or the host OS is not a Raspberry, the above bytes has not sent to KFive hardware.")
        if self.uart is not None:
            self.uart.write(bytesdata)

    @async_wrap
    def read_uart(self):
        if self.uart is None:
            return
        self.uart.reset_input_buffer()
        data = []
        while True:
            try:
                d = self.uart.read()
                s = ''
                if d == b'\xdd':
                    data.append(d)
                    s += d.hex()
                    g = 0
                    for _ in range(15):
                        d = self.uart.read()
                        data.append(d)
                        s += ' ' + d.hex()
                        if _ != 14:
                            g += int.from_bytes(d, 'big')
                    logger.log(f"SOne <-- KFive: {s}")
                    if (g-121)%256 != int.from_bytes(d, 'big'):
                        logger.error("KFive response checksum incorrect: %d vs %d" % ((g-121)%256, int.from_bytes(d, 'big')))
                    break
            except SerialException:
                continue

        self.time = int.from_bytes(data[2], 'big')
        self.read_temperature = int.from_bytes(data[7], 'big')
