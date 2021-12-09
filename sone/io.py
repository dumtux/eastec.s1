from sone.sone import SOne
from .conf import (
    UART_BAUDRATE,
    UART_EN_PIN,

    LED_R_1,
    LED_G_1,
    LED_B_1,
    LED_R_2,
    LED_G_2,
    LED_B_2,
    LED_MONO_1,
    LED_MONO_2,

    PWM_FREQ,
)
from .utils import Logger, is_raspberry


logger = Logger.instance()

if is_raspberry():
    # enable UART level shifter on RJ45 connector
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(UART_EN_PIN, GPIO.OUT)
    GPIO.output(UART_EN_PIN, GPIO.HIGH)

    if SOne.instance().pwm_dict is None:
        pwm_dict = dict()
        for pin in [LED_R_1, LED_G_1, LED_B_1, LED_R_2, LED_G_2, LED_B_2]:
            GPIO.setup(pin, GPIO.OUT)
            pwm_dict[pin] = GPIO.PWM(pin, PWM_FREQ)
            pwm_dict[pin].start(0)
        SOne.instance().pwm_dict = pwm_dict
else:
    GPIO = None
