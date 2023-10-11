import smbus
import time

SPEED_OF_SOUND = (343 * 100) / (1000 * 1000) # 343m/s to microseconds
# 343m/s * 100cm/m => 34300cm/s
# 34300cm/s / 1000ms/s => 34,3cm/ms
# 34,3cm/ms / 1000mus/ms => 0,00343 cm/mus

CMD_PWM1 = 0x04
CMD_PWM2 = 0x05
CMD_DIR1 = 0x06
CMD_DIR2 = 0x07
CMD_SONIC = 0X0C
SONIC_MAX_HIGH_BYTE = 100

PWM_MIN = 0
PWM_MAX = 1000

class CarShield:
	def __init__(self, bus, address = 0x18) -> None:
		self.bus = bus
		self.address = address

	def init(self) -> None:
		self.set_forward()
		self.stop()

	def _write_reg(self, reg, value):
		value = int(value)
		try:
			self.bus.write_i2c_block_data(self.address, reg, [value>>8,value&0xff])
			time.sleep(0.001)
			self.bus.write_i2c_block_data(self.address, reg, [value>>8,value&0xff])
			time.sleep(0.001)
			self.bus.write_i2c_block_data(self.address, reg, [value>>8,value&0xff])
			time.sleep(0.001)
		except Exception as e:
			print('I2C Error :', e)

	def _read_reg(self, reg):
		##################################################################################################
		#Due to the update of SMBus, the communication between Pi and the shield board is not normal.
		#through the following code to improve the success rate of communication.
		#But if there are conditions, the best solution is to update the firmware of the shield board.
		##################################################################################################
		for i in range(0, 10, 1):
			self.bus.write_i2c_block_data(self.address, reg, [0])
			a = self.bus.read_i2c_block_data(self.address, reg, 1)

			self.bus.write_byte(self.address, reg+1)
			b = self.bus.read_i2c_block_data(self.address, reg+1, 1)

			self.bus.write_byte(self.address, reg)
			c = self.bus.read_byte_data(self.address, reg)

			self.bus.write_byte(self.address, reg+1)
			d = self.bus.read_byte_data(self.address, reg+1)

			if a[0] == c and c < SONIC_MAX_HIGH_BYTE:
				return c<<8 | d
			else:
				continue
		return 0
		
	def read_distance(self, samples_to_average: int = 4) -> float:
		echo_time = 0.0
		for _ in range(samples_to_average):
			echo_time += self._read_reg(CMD_SONIC)
			time.sleep(0.0005) # 0.5ms

		echo_time /= samples_to_average # echo tme is in mus
		return (echo_time / 2.0) * SPEED_OF_SOUND # divide by 2 for back and forth distance, result is in cm
	
	def set_forward(self) -> None:
		self._write_reg(CMD_DIR1, 1)
		self._write_reg(CMD_DIR2, 1)

	def set_backward(self) -> None:
		self._write_reg(CMD_DIR1, 0)
		self._write_reg(CMD_DIR2, 0)

	def set_turn_left(self) -> None:
		self._write_reg(CMD_DIR1, 1)
		self._write_reg(CMD_DIR2, 0)

	def set_turn_right(self) -> None:
		self._write_reg(CMD_DIR1, 0)
		self._write_reg(CMD_DIR2, 1)

	def stop(self) -> None:
		self._write_reg(CMD_PWM1, PWM_MIN)
		self._write_reg(CMD_PWM2, PWM_MIN)

	def drive_diff(self, percentage_left: float, percentage_right: float) -> None:
		self._write_reg(CMD_PWM1, PWM_MAX * percentage_left)
		self._write_reg(CMD_PWM2, PWM_MAX * percentage_right)

	def drive(self, percentage: float) -> None:
		self.drive_diff(percentage, percentage)