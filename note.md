# Setting Up Pi as an A2DP Sink Device

## Enable USB Host

Enable USB Host of CM4.
The CM4 datasheet says:

> The USB interface is disabled to save power by default on the CM4 . To enable it you need to add
> `dtoverlay=dwc2,dr_mode=host` to the `config.txt` file

## Enable PCM5102 DAC

Add the following line to the `config.txt` file.

```
dtoverlay=hifiberry-dac
```

## Enable DS1307 RTC

https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time


## Reference

* [Raspberry Pi Compute Module 4 Datasheet](https://datasheets.raspberrypi.org/cm4/cm4-datasheet.pdf)
* [How to make various DACs work](https://github.com/guussie/PiDS/wiki/09.-How-to-make-various-DACs-work)
* [Adding a Real-Time Clock to Raspberry Pi](https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi)
* [Raspberry Pi Audio Receiver](https://github.com/nicokaiser/rpi-audio-receiver)
