import threading

import RPi.GPIO as GPIO
import time

step_down =  [
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

stepper_cat = [[12, 16, 18, 22], [], []]

stepper_but = [7, 11, 13, 15]

achieve_button = [40]

fail_button = [36]

servo_pwm = 12

achievement_flag = [False, False, False]

fail_flag = [False, False, False]

but_flag = False

cat_flag = False


def cat_move_runner(motor):

    while True:
        for pin in stepper_cat[motor]:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        for i in range(1200):
            for step in step_up:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)
            for step in step_up:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)
            time.sleep(0.08)

        for i in range(1450):
            for step in step_down:
                GPIO.output(stepper_cat[motor], step)
                time.sleep(0.001)
        GPIO.output(stepper_cat[motor], [0, 0, 0, 0])


def cat_move(motor):
    process = threading.Thread(target=cat_move_runner, args=(motor,))
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




def achievement_press(button, ev=None):
    global achievement_flag
    achievement_flag[button] = True
    print("press")


def fail_press(button, ev=None):
    global fail_flag
    fail_flag[button] = True
    print("press")


def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    for button in range(1):
        GPIO.setup(achieve_button[button], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(fail_button[button], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(achieve_button[button], GPIO.RISING, callback=lambda x: achievement_press(button),
                              bouncetime=50)
        GPIO.add_event_detect(fail_button[button], GPIO.RISING, callback=lambda y: fail_press(button),
                              bouncetime=50)

        cat_move(0)

