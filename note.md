# Setting Up CM4 on Eastec K9 Board


## Enable USB Host

Enable USB Host of CM4.
The CM4 datasheet says:

> The USB interface is disabled to save power by default on the CM4 . To enable it you need to add
> `dtoverlay=dwc2,dr_mode=host` to the `/boot/config.txt` file

For more information, read the datasheet ([1]).


## Enable PCM5102 DAC

Add the following line to the `/boot/config.txt` file.
```
dtoverlay=hifiberry-dac
```

Disable the default HDMI audio output (this is critical for Bluetooth A2DP Sink setup) by commenting the following line
```
#dtparam=audio=on
```

For more information, read the article ([2]).


## Enable DS1307 RTC

Add the following line to the `/boot/config.txt` file.
```
dtoverlay=i2c-rtc,ds1307
```

Reboot and see `UU` is showed up by `i2cdetect` command
```sh
sudo i2cdetect -y 1
```

Remove and disable *fake hwclock*
```sh
sudo apt-get -y remove fake-hwclock
sudo update-rc.d -f fake-hwclock remove
sudo systemctl disable fake-hwclock
```

Edit `/lib/udev/hwclock-set` and comment these 5 lines
```
...
#if [ -e /run/systemd/system ] ; then
# exit 0
#fi
...
#/sbin/hwclock --rtc=$dev --systz --badyear
...
#/sbin/hwclock --rtc=$dev --systz
...
```

Sync time from Pi to RTC
```sh
sudo hwclock -r
# if time is not correct, set it manually before writing
sudo hwclock -w
```

For more information, read the article ([3]).


## Bluetooth A2DP Sink Setup

Install [Bluealsa](https://github.com/raspberrypi-ui/bluealsa)
```sh
sudo apt install bluealsa
```


Edit `/lib/systemd/system/bluealsa.service` file, the last line as
```
ExecStart=/usr/bin/bluealsa --profile=a2dp-sink
```

Create Systemd service file on `/etc/systemd/system/aplay.service`
```
[Unit]
Description=BlueALSA aplay service
After=bluetooth.service
Requires=bluetooth.service

[Service]
ExecStart=/usr/bin/bluealsa-aplay 00:00:00:00:00:00

[Install]
WantedBy=multi-user.target
```

Run the service
```
sudo systemctl enable aplay
```

After rebooting, set the Bluetooth as *discoverable* on the system tray icon.
Now the CM4 is recognized as a valid Bluetooth audio device from any phone.

But the sound will only be outputed via default HDMI audio if it is not disabled correctly on `/boot/config.txt`.
If the sound only comes out from HDMI display, check if PCM5102 (hifiberry) is set as the default audio output.
It should show only one audio device like `card 0: sndrpihifiberry [snd_rpi_hifiberry_dac], ...`
```sh
aplay -l
```

For more information, read the article ([4]).


## Bluetooth GPIO Control Alongside A2DP

While the K9 is connected as an A2DP Sink device and being streamed audio,
it is possible to receive control data.

Install [BlueDot](https://github.com/martinohanlon/BlueDot)
```
sudo pip3 install bluedot
```

Install BlueDot Android app and do testing.
```python
from bluedot import BlueDot
bd = BlueDot()
while(bd.wait_for_press()):
    print("You pressed the blue dot!")
```

For more information, read the doc ([5]).


## Hide Mouse Cursor

Add the following line to `[Seat*]` section of `/etc/lightdm/lightdm.conf` file.

```
xserver-command = X -nocursor
```

For more information, read the QA ([6]).


## Change Bluetooth Device Name

Create file `/etc/machine-info` with,

```
PRETTY+HOSTNAME=Eastec-SOne
```

To apply this, need to restart the system, or restart the Bluetooth service.

```sh
sudo service bluetooth restart
```


## Reference

* (1) [Raspberry Compute Module 4 Datasheet][1]
* (2) [How to make various DACs work][2]
* (3) [Adding a Real-Time Clock to Raspberry Pi][3]
* (4) [Raspberry Pi 3 Bluetooth A2DP Sink/Reciever Setup Problem][4]
* (5) [Blue Dot Documentation][5]

[1]: <https://datasheets.raspberrypi.org/cm4/cm4-datasheet.pdf> "Raspberry CM4 Datasheet"
[2]: <https://github.com/guussie/PiDS/wiki/09.-How-to-make-various-DACs-work> "How to make various DACs work"
[3]: <https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi> "Adding a Real-Time Clock to Raspberry Pi"
[4]: <https://www.raspberrypi.org/forums/viewtopic.php?t=161770> "Raspberry Pi 3 Bluetooth A2DP Sink/Reciever Setup Problem"
[5]: <https://bluedot.readthedocs.io/en/latest/> "Raspberry Pi 3 BlueDot Documentation"
[6]: <https://raspberrypi.stackexchange.com/questions/53127/how-to-permanently-hide-mouse-pointer-or-cursor-on-raspberry-pi> "How to permanently hide mouse pointer or cursor on Raspberry PI?"
