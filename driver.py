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

DIRECTIONS = 24
def heading_to_direction(heading):
    return int(round(heading / (360.0 / DIRECTIONS))) % DIRECTIONS

def get_difference(desired_heading, current_heading):
    difference = heading_to_direction(desired_heading) - heading_to_direction(current_heading)
    if difference > DIRECTIONS // 2:
        difference -= DIRECTIONS
    if difference < - DIRECTIONS // 2:
        difference += DIRECTIONS
    return difference

def turn_left(desired_heading, speed=0.4):
    heading = compass.read_heading()
    difference = get_difference(desired_heading, heading)
    
    car_shield.set_turn_left()
    car_shield.drive(speed)
    while difference < 0:
        heading = compass.read_heading()
        difference = get_difference(desired_heading, heading)
        if abs(difference) <= 2:
            car_shield.drive(speed * 0.75)
        print('Left Turn', 'Heading', heading, 'Difference Directions', difference, 'Difference Degrees', difference * DIRECTIONS)
        time.sleep(0.05)

    car_shield.stop()
    car_shield.set_forward()

def turn_right(desired_heading, speed=0.4):
    heading = compass.read_heading()
    difference = get_difference(desired_heading, heading)
    
    car_shield.set_turn_right()
    car_shield.drive(speed)
    while difference > 0:
        heading = compass.read_heading()
        difference = get_difference(desired_heading, heading)
        if abs(difference) <= 2:
            car_shield.drive(speed * 0.75)
        print('Right Turn', 'Heading', heading, 'Difference Directions', difference, 'Difference Degrees', difference * DIRECTIONS)
        time.sleep(0.05)

    car_shield.stop()
    car_shield.set_forward()

def turn(desired_heading, speed=0.4):
    heading = compass.read_heading()
    difference = get_difference(desired_heading, heading)
    print('Difference', difference)

    if difference < 0:
        turn_left(desired_heading, speed)
    if difference > 0:
        turn_right(desired_heading, speed)

def right_corner():
    heading = compass.read_heading()
    desired_heading = (heading + 90 + 360) % 360
    turn(desired_heading)

def left_corner():
    heading = compass.read_heading()
    desired_heading = (heading - 90 + 360) % 360
    turn(desired_heading)

def has_distance(distance = 10):
    d = car_shield.read_distance()
    return (d == 0) or d > distance

def drive(sec = 2):
    start_heading = compass.read_heading()
    car_shield.set_forward()
    car_shield.drive()
    stop = time.time() + sec
    while (stop > time.time()) and has_distance():
        heading = compass.read_heading()
        difference = get_difference(start_heading, heading)
        if difference < 0:
            car_shield.drive_diff(0.4, 0.5)
        if difference > 0:
            car_shield.drive_diff(0.5, 0.4)

        time.sleep(0.05)
    car_shield.stop()

def calibrate():
    if random.random() > 0.5:
        car_shield.set_turn_right()
    else:
        car_shield.set_turn_left()

    car_shield.drive()
    for _ in range(100):
        compass.read_heading()
        time.sleep(0.1)

    car_shield.stop()
    car_shield.set_forward()

if __name__ == '__main__':
    try:
        calibrate()

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