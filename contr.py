import threading

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    import mock_GPIO as GPIO

    print("No RPi.GPIO found")

import time

# half steps for stepper motor
step_down = [
    [1, 0, 0, 1], [1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0],
    [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1]
]

step_up = [
    [0, 0, 0, 1], [0, 0, 1, 1], [0, 0, 1, 0], [0, 1, 1, 0],
    [0, 1, 0, 0], [1, 1, 0, 0], [1, 0, 0, 0], [1, 0, 0, 1]
]

# pins for the three stepper motors driving the caterpillars
stepper_cat = [[12, 16, 18, 22], [0, 0, 0, 0], [0, 0, 0, 0]]

# pins for the stepper motor driving the butterfly
stepper_but = [7, 11, 13, 15]

# distance caterpillars need to travel
length = 800


# function moving the caterpillar selected eiter up or down
def cat_move_runner(up, motor):
    for pin in stepper_cat[motor]:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

    if up:
        for i in range(length // 2):
            for step in step_up:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)
            for step in step_up:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)
            time.sleep(0.08)

    else:
        for i in range(length):
            for step in step_down:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)

    GPIO.output(stepper_cat[motor], [0, 0, 0, 0])


# function to move caterpillar in new thread
def cat_move(up, motor):
    process = threading.Thread(target=cat_move_runner, args=(up, motor,))
    process.start()


# function moving the butterfly selected
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


# function to move caterpillar in new thread
def butterfly_move():
    process_butterfly = threading.Thread(target=butterfly_move_runner)
    process_butterfly.start()


def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
