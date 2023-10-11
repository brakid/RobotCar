import smbus
import time
import math
import statistics

DATA_REGISTER = 0x00
DATA_REGISTER_COUNT = 6
STATUS_REGISTER = 0x06
CONFIG_REGISTER_1 = 0x09
CONFIG_REGISTER_2 = 0x0A
RESET_REGISTER = 0x0B

# config register values
STANDBY_MODE =          0b00 << 0
CONTINUOUS_MODE =       0b01 << 0
DATA_RATE_10 =          0b00 << 2
DATA_RATE_50 =          0b01 << 2
DATA_RATE_100 =         0b10 << 2
DATA_RATE_200 =         0b11 << 2
GAUSS_2 =               0b00 << 4
GAUSS_8 =               0b01 << 4
OVERSAMPLING_512 =      0b00 << 6
OVERSAMPLING_256 =      0b01 << 6
OVERSAMPLING_128 =      0b10 << 6
OVERSAMPLING_64 =       0b11 << 6
CONFIG_REGISTER_VALUE = CONTINUOUS_MODE | DATA_RATE_200 | GAUSS_8 | OVERSAMPLING_512

class Compass:
	def __init__(self, bus, address = 0x0d, declination = 2.77, offset = 180) -> None: #https://www.magnetic-declination.com/Luxembourg/Letzeburg/1528005.html
		self.bus = bus
		self.address = address
		self.declination = declination
		self.offset = offset
		self.x_high = float('-inf')
		self.x_low = float('inf')
		self.y_high = float('-inf')
		self.y_low = float('inf')

	def init(self) -> None:
		self.bus.write_byte_data(self.address, RESET_REGISTER, 0x01)
		time.sleep(0.01)
		self.bus.write_byte_data(self.address, CONFIG_REGISTER_1, CONFIG_REGISTER_VALUE)
		self.bus.write_byte_data(self.address, CONFIG_REGISTER_2, 0x00)
		time.sleep(0.01)

	def _convert(self, high_byte: int, low_byte: int) -> int:
		value = ((high_byte << 8) | low_byte)

		if(value > 0x7fff):
			value = value - 0x10000
		return value
	
	def _scale(self, value: float, value_high: float, value_low: float) -> float:
		if (value_low == value_high):
			return 0
		return (value - (value_high + value_low) / 2.0) / (value_high - value_low)
	
	def _calculate_heading(self, x: float, y: float) -> float:
		return (math.degrees(math.atan2(y, x)) + self.declination + self.offset + 360) % 360
	
	def _update_x(self, x: float) -> None:
		if x < self.x_low:
			self.x_low = x

		if x > self.x_high:
			self.x_high = x

	def _update_y(self, y: float) -> None:
		if y < self.y_low:
			self.y_low = y

		if y > self.y_high:
			self.y_high = y

	def read_xyz(self) -> (int, int, int):
		[x_l, x_h, y_l, y_h, z_l, z_h ] = self.bus.read_i2c_block_data(self.address, DATA_REGISTER, DATA_REGISTER_COUNT)
		x = self._convert(x_h, x_l)
		y = self._convert(y_h, y_l)
		z = self._convert(z_h, z_l)

		return (x, y, z)
	
	def read_heading_single(self) -> int:
		x, y, _ = self.read_xyz()

		self._update_x(x)
		self._update_y(y)		

		x = self._scale(x, self.x_high, self.x_low)
		y = self._scale(y, self.y_high, self.y_low)
	
		return self._calculate_heading(x, y)
	
	def read_heading(self, samples_to_average = 5):
		self.read_heading_single()
		time.sleep(0.005)
		headings = []
		for _ in range(samples_to_average):
			headings.append(self.read_heading_single())
			time.sleep(0.005)
		return statistics.median(headings)