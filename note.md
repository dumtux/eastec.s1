# Setting Up Pi as an A2DP Sink Device

## Initial Setup

Enable USB Host of CM4.
The CM4 datasheet says:

> The USB interface is disabled to save power by default on the CM4 . To enable it you need to add
> `dtoverlay=dwc2,dr_mode=host` to the `config.txt` file

Enable PCM5102.
Add the following line to the `config.txt` file.

```
dtoverlay=hifiberry-dac
```


## Reference

* [Raspberry Pi Audio Receiver](https://github.com/nicokaiser/rpi-audio-receiver)
