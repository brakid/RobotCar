import smbus
import time
import random
from compass import Compass
from car_shield import CarShield
from distance import Distance

DIRECTIONS = 36

def normalize(angle):
    return (angle + 360) % 360

def heading_to_direction(heading):
    return int(round(heading / (360.0 / DIRECTIONS))) % DIRECTIONS

def get_difference(desired_heading, current_heading):
    difference = heading_to_direction(desired_heading) - heading_to_direction(current_heading)
    if difference > DIRECTIONS // 2:
        difference -= DIRECTIONS
    if difference < - DIRECTIONS // 2:
        difference += DIRECTIONS
    return difference

class Driver:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.bus.open(1)
        self.compass = Compass(self.bus)
        self.compass.init()

        self.car_shield = CarShield(self.bus)
        self.car_shield.init()

        self.distance = Distance()

        # keep track of the global north
        self.north = None
        self.stop()

    def stop(self):
        self.car_shield.stop()

    def turn_left(self, desired_heading, speed=0.4):
        heading = self.compass.read_heading()
        difference = get_difference(desired_heading, heading)
        
        self.car_shield.set_turn_left()
        self.car_shield.drive(speed)
        while difference < 0:
            heading = self.compass.read_heading()
            difference = get_difference(desired_heading, heading)
            if abs(difference) <= 2:
                self.car_shield.drive(speed * 0.75)
            #print('Left Turn', 'Heading', heading, 'Difference Directions', difference, 'Difference Degrees', difference * DIRECTIONS)
            time.sleep(0.05)

        self.car_shield.stop()
        self.car_shield.set_forward()

    def turn_right(self, desired_heading, speed=0.4):
        heading = self.compass.read_heading()
        difference = get_difference(desired_heading, heading)
        
        self.car_shield.set_turn_right()
        self.car_shield.drive(speed)
        while difference > 0:
            heading = self.compass.read_heading()
            difference = get_difference(desired_heading, heading)
            if abs(difference) <= 2:
                self.car_shield.drive(speed * 0.75)
            #print('Right Turn', 'Heading', heading, 'Difference Directions', difference, 'Difference Degrees', difference * DIRECTIONS)
            time.sleep(0.05)

        self.car_shield.stop()
        self.car_shield.set_forward()

    def turn(self, desired_heading, speed=0.4, adjustments=3):
        heading = self.compass.read_heading()
        difference = get_difference(desired_heading, heading)
        #print('Difference', difference)

        if difference < 0:
            self.turn_left(desired_heading, speed)
        if difference > 0:
            self.turn_right(desired_heading, speed)

        # allow to bounce back and forth when aiming at the desired angle
        if adjustments > 0:
            self.turn(desired_heading, speed * 0.95, adjustments-1)

    def has_distance(self, distance = 20):
        d = self.get_distance()
        cont = (d == 0) or (d > distance)
        #print('Distance', d, 'Continue', cont)
        return cont

    def drive(self, sec = 2, speed = 0.4):
        start_heading = self.compass.read_heading()
        self.car_shield.set_forward()
        self.car_shield.drive()
        stop = time.time() + sec
        while (stop > time.time()) and self.has_distance():
            heading = self.compass.read_heading()
            difference = get_difference(start_heading, heading)
            if difference < 0:
                #print('Correct to right')
                self.car_shield.drive_diff(speed * 1.1, speed)
            if difference > 0:
                #print('Correct to left')
                self.car_shield.drive_diff(speed, speed * 1.1)

            time.sleep(0.01)
        self.car_shield.stop()
        #print('Stopped')

    def calibrate(self):
        if random.random() > 0.5:
            self.car_shield.set_turn_right()
        else:
            self.car_shield.set_turn_left()

        self.car_shield.drive()
        for _ in range(100):
            self.compass.read_heading()
            time.sleep(0.1)

        self.car_shield.stop()
        self.car_shield.set_forward()

    # manually move the car to face the normalized north.
    def set_north(self):
        north_heading = self.compass.read_heading()
        print(f'Defining {north_heading} as north')
        self.north = north_heading

    def read_heading(self):
        if self.north is None:
            raise Exception('No north set')
        
        heading = self.compass.read_heading()
        return normalize(heading - self.north)
    
    def get_distance(self):
        return self.distance.get_distance()

    def turn_north(self, desired_heading):
        self.turn(normalize(desired_heading + self.north))

if __name__ == '__main__':
    try:
        driver = Driver()
        driver.calibrate()

        input('Face north')

        driver.set_north()

        home_heading = driver.read_heading()
        print('Home', home_heading)

        time.sleep(1)

        desired_heading = normalize(home_heading - 179)
        print('Desired', desired_heading)
        driver.turn_north(desired_heading)

        while True:
            heading = driver.read_heading()
            distance = driver.read_distance()
            print(heading, '°', distance, 'cm')
            time.sleep(0.5)
    except:
        driver.stop()