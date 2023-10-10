import smbus
import time
import math
import random
from compass import Compass
from car_shield import CarShield

bus = smbus.SMBus(1)
bus.open(1)
compass = Compass(bus)
compass.init()

car_shield = CarShield(bus)
car_shield.init()

def get_difference(desired_heading, current_heading):
    difference = desired_heading - current_heading
    if difference > 180:
        difference -= 360.0
    if difference < -180:
        difference += 360.0
    return difference

def turn_left(desired_heading):
    heading = compass.read_heading()
    difference = get_difference(desired_heading, heading)
    
    car_shield.set_turn_left()
    while difference < 0:
        car_shield.stop()
        time.sleep(0.01)
        heading = compass.read_heading()
        difference = get_difference(desired_heading, heading)
        print('Difference', difference)
        car_shield.drive()
        time.sleep(0.05)

    car_shield.stop()
    car_shield.set_forward()

def turn_right(desired_heading):
    heading = compass.read_heading()
    difference = get_difference(desired_heading, heading)
    
    car_shield.set_turn_right()
    while difference > 0:
        car_shield.stop()
        time.sleep(0.01)
        heading = compass.read_heading()
        difference = get_difference(desired_heading, heading)
        print('Difference', difference)
        car_shield.drive()
        time.sleep(0.05)

    car_shield.stop()
    car_shield.set_forward()

def turn(desired_heading):
    heading = compass.read_heading()

    difference = get_difference(desired_heading, heading)

    print('Difference', difference)

    if difference < 0:
        turn_left(desired_heading)
    if difference > 0:
        turn_right(desired_heading)

def right_corner():
    heading = compass.read_heading()
    desired_heading = (heading + 90 + 360) % 360
    turn(desired_heading)

def left_corner():
    heading = compass.read_heading()
    desired_heading = (heading - 90 + 360) % 360
    turn(desired_heading)

def calibrate():
    if random.random() > 0.5:
        car_shield.set_turn_right()
    else:
        car_shield.set_turn_left()

    for _ in range(50):
        car_shield.stop()
        time.sleep(0.01)
        compass.read_heading()
        car_shield.drive()
        time.sleep(0.1)

    car_shield.stop()
    car_shield.set_forward()

if __name__ == '__main__':
    try:
        car_shield.set_turn_right()
        #car_shield.set_turn_left()
        car_shield.drive()
        for _ in range(100):
            compass.read_heading()
            time.sleep(0.01)
        car_shield.stop()
        car_shield.set_forward()

        home_heading = compass.read_heading()
        print('Home', home_heading)

        time.sleep(1)

        desired_heading = (home_heading - 179 + 360) % 360
        print('Desired', desired_heading)
        turn(desired_heading)

        while True:
            heading = compass.read_heading()
            distance = car_shield.read_distance()
            print(heading, '°', distance, 'cm')
            time.sleep(0.5)
    except:
        car_shield.stop()