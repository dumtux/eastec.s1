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

    pwm = dict()
    for pin in [LED_R_1, LED_G_1, LED_B_1, LED_R_2, LED_G_2, LED_B_2]:
        GPIO.setup(pin, GPIO.OUT)
        pwm[pin] = GPIO.PWM(pin, PWM_FREQ)
        pwm[pin].start(0)

    def light_rgb_1(r: int, g: int, b: int):
        if (r not in range(256)) or (g not in range(256)) or (b not in range(256)):
            raise Exception("RGB values should be 0-255")
        pwm[LED_R_1].ChangeDutyCycle(int(r / 255 * 100))
        pwm[LED_G_1].ChangeDutyCycle(int(g / 255 * 100))
        pwm[LED_B_1].ChangeDutyCycle(int(b / 255 * 100))

    def light_rgb_2(r: int, g: int, b: int):
        if (r not in range(256)) or (g not in range(256)) or (b not in range(256)):
            raise Exception("RGB values should be 0-255")
        pwm[LED_R_2].ChangeDutyCycle(int(r / 255 * 100))
        pwm[LED_G_2].ChangeDutyCycle(int(g / 255 * 100))
        pwm[LED_B_2].ChangeDutyCycle(int(b / 255 * 100))
else:
    GPIO = None

    def light_rgb_1(r: int, g: int, b: int):
        logger.warn("Host is not Raspberry OS. Ignoring Light 1 PWM command.")

    def light_rgb_2(r: int, g: int, b: int):
        logger.warn("Host is not Raspberry OS. Ignoring Light 2 PWM command.")
