import serial

ser = serial.Serial(port='/dev/ttyUSB0', baudrate=4800, timeout=1)
i = 0
while True:
    d = ser.read()
    s = ''
    if d == b'\xdd':
        s += d.hex()
        g = 0
        for _ in range(15):
            d = ser.read()
            s += ' ' + d.hex()
            if _ != 14:
                g += int.from_bytes(d, 'big')
        print(f'box2panel {i:04} ', s)
        try:
            assert (g-121)%256 == int.from_bytes(d, 'big')
        except:
            print("checksum incorrect", (g-121)%256, int.from_bytes(d, 'big'))
        i += 1
    elif d == b'\xcc':
        s += d.hex()
        g = 0
        for _ in range(15):
            d = ser.read()
            s += ' ' + d.hex()
            if _ != 14:
                g += int.from_bytes(d, 'big')
        print(f'panel2box {i:04} ', s)
        assert (g-138)%256 == int.from_bytes(d, 'big')
        i += 1
    else:
        pass
