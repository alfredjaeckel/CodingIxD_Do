import multiprocessing

import RPi.GPIO as GPIO
import time

step_down = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]
step_up = [
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1]
]

stepper = [[7, 11, 13, 15], [], []]

achieve_button = [40]

fail_button = [36]

achievement_flag = [False, False, False]

fail_flag = [False, False, False]


def cat_move_runner(up, motor):

    for pin in stepper[motor]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)
    if up:
        steps = step_up
    else:
        steps = step_down

    for i in range(100):
        for step in steps:
            GPIO.output(stepper[motor], step)
            time.sleep(0.001)

    GPIO.output(stepper[motor], [0, 0, 0, 0])


def cat_move(up, motor):
    process = multiprocessing.Process(target=cat_move_runner, args=(up, motor,))
    process.start()


def achievement_press(button, ev=None):
    global achievement_flag
    achievement_flag[button] = True


def fail_press(button, ev=None):
    global fail_flag
    fail_flag[button] = True


def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    for button in range(1):
        GPIO.setup(achieve_button[button], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(fail_button[button], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(achieve_button[button], GPIO.RISING, callback=lambda x: achievement_press(button),
                              bouncetime=50)
        GPIO.add_event_detect(fail_button[button], GPIO.RISING, callback=lambda y: fail_press(button),
                              bouncetime=50)

