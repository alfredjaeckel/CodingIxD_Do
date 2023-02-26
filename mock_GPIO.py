'''
    Mock GPIO to allow for testing without raspberry pi
'''

OUT = None
BOARD = None



def setup(arg0=None, arg1=None, arg2=None):
    print("GPIO.setup")


def output(arg0=None, arg1=None, arg2=None):
    print("GPIO output")


def setmode(arg0=None, arg1=None, arg2=None):
    print("GPIO setmode")
