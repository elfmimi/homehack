import time
from machine import Pin
p4 = Pin(4, Pin.OUT)
p5 = Pin(5, Pin.IN, Pin.PULL_UP)
p4.low()


def switch(value):
    if value != 0:
        value = 1
    if p5.value() == value:
        print('(no need)')
        state()
    else:
        for i in range(3):
            if i != 0:
                print('RETRY')
            p4.high()
            time.sleep_ms(300)
            p4.low()
            for j in range(20):
                time.sleep_ms(100)
                if p5.value() == value:
                    print('OK')
                    state()
                    return
        print('NG')
        state()


def on():
    switch(0)


def off():
    switch(1)


def state():
    if p5.value() == 0:
        print('ON')
    else:
        print('OFF')
