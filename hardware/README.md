# Hardware Designs

## known Issues of K9 Baseboard v1

* 4 inductors of power amplifier are too hot on idle status
* **Active** and **Power** LEDs are wired to GND, not working
* TX/RX LEDs are wired to GND, being always ON while UART idle status
* RX(GPIO15) is wired wrongly, makes the CM4 rebooted via RX signal
* PCM5122 (hifiberry-dacplus like) ADDR0 pin is wired wrongly and did not worked even after temporal fixing
* RTC is missing


## Known Issues of K9 Base v2

* 4 inductors of power amplifier are too hot on idle status
* **Active** and **Power** indicator LEDs are in wrong color. Need to use green for **Power** and yellow for **Active** led.
