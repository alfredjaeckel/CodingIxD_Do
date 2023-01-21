import RPi.GPIO as GPIO
import time


# raspberry GPIO


def move():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    control_pins = [7, 11, 13, 15]
    for pin in control_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    halfstep_seq = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1]
    ]
    halfstep2_seq = [
        [0, 0, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 0],
        [1, 1, 0, 0],
        [1, 0, 0, 0],
        [1, 0, 0, 1]
    ]

    while True:
        for i in range(200):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(control_pins[pin], halfstep2_seq[halfstep][pin])
            time.sleep(0.002)

        for i in range(200):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(control_pins[pin], halfstep_seq[halfstep][pin])
            time.sleep(0.002)
        time.sleep(1)
    GPIO.cleanup()

