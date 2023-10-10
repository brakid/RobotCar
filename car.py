from mDev3 import mDEV
import time

m = mDEV()

def stop():
	m.write_reg(m.CMD_PWM1, 0)
	m.write_reg(m.CMD_PWM2, 0)

def forward():
	m.write_reg(m.CMD_DIR1, 1)
	m.write_reg(m.CMD_DIR2, 1)
	m.write_reg(m.CMD_PWM1, 400)
	m.write_reg(m.CMD_PWM2, 400)

def turn_left():
	m.write_reg(m.CMD_DIR1, 1)
	m.write_reg(m.CMD_DIR2, 0)
	m.write_reg(m.CMD_PWM1, 400)
	m.write_reg(m.CMD_PWM2, 400)
	time.sleep(0.55)
	m.write_reg(m.CMD_PWM1, 0)
	m.write_reg(m.CMD_PWM2, 0)

def turn_right():
        m.write_reg(m.CMD_DIR1, 0)
        m.write_reg(m.CMD_DIR2, 1)
        m.write_reg(m.CMD_PWM1, 400)
        m.write_reg(m.CMD_PWM2, 400)
        time.sleep(0.55)
        m.write_reg(m.CMD_PWM1, 0)
        m.write_reg(m.CMD_PWM2, 0)

stop()

distance = m.get_distance()
print(distance)
while distance > 20 or distance < 1:
    print('Distance:', distance, 'cm')
    forward()
    time.sleep(0.05)
    distance = m.get_distance()
    if distance <= 20:
        turn_left()
    distance = m.get_distance()

stop()