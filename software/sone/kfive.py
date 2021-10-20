from typing import Callable

from .singletone import Singleton
from .models import Status


class KFive(Singleton):
    HEATER_VALS = {0: 0, 1: 30, 2: 50, 3: 70, 4: 100}

    heater: bool  = False  # on/off, determined by set temperature vs read temperature, set time vs ellapsed time
    pwr: bool  = False     # on/off
    lac: bool  = False     # on/off
    l1_mode: int  = 0      # 0 - 8
    l2: bool  = False      # on/off
    temp: int  = 0         # temperature 20 - 70
    time: int  = 0         # minutes 0 - 90
    auto_hh: int  = 0      # automode hour 0 - 23
    auto_mm: int  = 0      # automode minute 0 - 59
    ht1: int  = 0          # heater 1 level 0 - 4, 0-0%, 1-30%, 2-50%, 3-75$, 4-100%
    ht2: int  = 0          # heater 2 level 0 - 4
    ht3: int  = 0          # heater 3 level 0 - 4

    def to_bytes(self) -> bytes:
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

    def update(status: Status) -> Status:
        self.temp = status.target_temperature
        self.time = status.target_timer

    def write(self):
        # data = self.to_bytes()
        # s.write(data)
        raise Exception("Not implemented yet")

    def read(self, callback: Callable):
        raise Exception("Not implemented yet")
