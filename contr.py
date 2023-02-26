import threading

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    import mock_GPIO as GPIO
    print("No RPi.GPIO found")

import time

step_down = [
    [1,0,0,1],
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1]
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

stepper_cat = [[12, 16, 18, 22], [0,0,0,0], [0,0,0,0]]

stepper_but = [7, 11, 13, 15]

achieve_button = [40]

fail_button = [36]

servo_pwm = 12

achievement_flag = [False, False, False]

fail_flag = [False, False, False]

but_flag = False

cat_flag = False


def cat_move_runner(up, motor):

    for pin in stepper_cat[motor]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    if up:
        for i in range(1600):
            for step in step_up:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)
            for step in step_up:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)
            time.sleep(0.08)

    else:
        for i in range(1600):
            for step in step_down:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)

    GPIO.output(stepper_cat[motor], [0, 0, 0, 0])


def cat_move(up, motor):
    process = threading.Thread(target=cat_move_runner, args=(up, motor,))
    process.start()
    print("cat is moving")


def butterfly_move_runner():

    for pin in stepper_but:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    delay = 0.001

    for i in range(280):
        for step in step_down:
            GPIO.output(stepper_but, step)
            time.sleep(delay)

    time.sleep(10)

    for i in range(280):
        for step in step_up:
            GPIO.output(stepper_but, step)
            time.sleep(delay)

    GPIO.output(stepper_but, [0, 0, 0, 0])



def butterfly_move():
    process_butterfly = threading.Thread(target=butterfly_move_runner)
    print("butterfly will be moving")
    process_butterfly.start()
    print("butterfly is moving")


def init_GPIO():
    GPIO.setmode(GPIO.BOARD)

