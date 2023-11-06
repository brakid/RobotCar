import smbus
import time

CMD_PWM1 = 0x04
CMD_PWM2 = 0x05
CMD_DIR1 = 0x06
CMD_DIR2 = 0x07

PWM_MIN = 0
PWM_MAX = 1000

class CarShield:
	def __init__(self, bus, address = 0x18) -> None:
		self.bus = bus
		self.address = address

	def init(self) -> None:
		self.set_forward()
		self.stop()

	def _write_reg(self, reg: int, value: int) -> None:
		self.bus.write_i2c_block_data(self.address, reg, [value>>8,value&0xff])

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
		self._write_reg(CMD_PWM1, int(PWM_MAX * percentage_left))
		self._write_reg(CMD_PWM2, int(PWM_MAX * percentage_right))

	def drive(self, percentage: float = 0.4) -> None:
		self.drive_diff(percentage, percentage)