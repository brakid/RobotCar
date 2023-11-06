import time
import RPi.GPIO as GPIO
import statistics

SPEED_OF_SOUND = (343 * 100) # 343m/s to cm/s
# 343m/s * 100cm/m => 34300cm/s

class Distance():
    def __init__(self, trigger = 16, echo = 18):
        self.trigger = trigger
        self.echo = echo
        
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, 0)

    def _measure(self):
        GPIO.output(self.trigger, 1)
        time.sleep(0.00001)
        GPIO.output(self.trigger, 0)
        start = time.time()
        while GPIO.input(self.echo) == 0:
            start = time.time()
        while GPIO.input(self.echo) == 1:
            stop = time.time()
        elapsed = stop - start
        distance = (elapsed / 2.0) * SPEED_OF_SOUND
        return distance

    def get_distance(self, samples = 10):
        distances = []
        for _ in range(samples):
            distances.append(self._measure())
            time.sleep(0.005)
        return statistics.median(distances)