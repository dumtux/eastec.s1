from typing import Callable

from .singletone import Singleton
from .models import Status


class KFive(Singleton):
    HEATER_VALS = {0: 0, 1: 30, 2: 50, 3: 70, 4: 100}

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

    def to_bytes(self) -> bytes:
        a = []
        a.append(0xcc)
        a.append((self.heater * 1 + self.lac * 2 + self.l2 * 4) * 0x10 + (1 if self.pwr else 9))
        a.append(self.time)
        a.append(self.auto_hh)
        a.append(self.auto_mm)
        a.append(self.target_temperature)
        a.append(int(self.target_temperature * 9 / 5) + 32)
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
        print(t)
        ba = bytearray.fromhex(t)
        return bytes(ba)

    def update(self, status: Status) -> Status:
        self.target_temperature = status.target_temperature
        self.time = status.target_timer
        self.ht1 = status.heaters[0].level
        self.ht2 = status.heaters[1].level
        self.ht3 = status.heaters[2].level

        if self.time == 0:
            self.pwr = False
            self.heater = False
            self.endbyte = 0x42
            status.state = 'standby'
        else:
            if status.state == 'standby':
                self.pwr = False
                self.heater = False
                self.endbyte = 0x42
            elif status.state == 'playing':
                self.pwr = True
                self.heater = self.target_temperature > self.read_temperature
                self.endbyte = 0xC2 if self.heater else 0x02
            elif status.state == 'paused':
                self.pwr = False
                self.heater = False
                self.endbyte = 0x42

        return status

    def sync_hardware(self):
        self.uart.write(self.to_bytes())
