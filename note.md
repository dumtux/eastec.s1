# Setting Up CM4 on Eastec K9 Board


## Enable USB Host

Enable USB Host of CM4.
The CM4 datasheet says:

> The USB interface is disabled to save power by default on the CM4 . To enable it you need to add
> `dtoverlay=dwc2,dr_mode=host` to the `/boot/config.txt` file

For more information, read [Raspberry Compute Module 4 Datasheet][1].


## Enable PCM5102 DAC

Add the following line to the `/boot/config.txt` file.
```
dtoverlay=hifiberry-dac
```

Disable the default HDMI audio output (this is critical for Bluetooth A2DP Sink setup) by commenting the following line
```
#dtparam=audio=on
```

For more information, read [How to make various DACs work][2].


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

For more information, read [Adding a Real-Time Clock to Raspberry Pi][3].


## Bluetooth A2DP Sink Setup

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

For more information, read [Raspberry Pi 3 Bluetooth A2DP Sink/Reciever Setup Problem][4]


## Reference

* [1]: <https://datasheets.raspberrypi.org/cm4/cm4-datasheet.pdf> "Raspberry CM4 Datasheet"
* [2]: <https://github.com/guussie/PiDS/wiki/09.-How-to-make-various-DACs-work> "How to make various DACs work"
* [3]: <https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi> "Adding a Real-Time Clock to Raspberry Pi"
* [4]: <https://www.raspberrypi.org/forums/viewtopic.php?t=161770> "Raspberry Pi 3 Bluetooth A2DP Sink/Reciever Setup Problem"
