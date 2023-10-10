#-*- coding: utf-8 -*-
"""
 ******************************************************************************
 * File  mDev.py
 * Author  Freenove (http://www.freenove.com)
 * Date    2016/11/14
 ******************************************************************************
 * Brief
 *   This is the Class mDev. Used for Control the Shield.
 ******************************************************************************
 * Copyright
 *   Copyright © Freenove (http://www.freenove.com)
 * License
 *   Creative Commons Attribution ShareAlike 3.0
 *   (http://creativecommons.org/licenses/by-sa/3.0/legalcode)
 ******************************************************************************
"""
import smbus
import time

SPEED_OF_SOUND = (343 * 100) / (1000 * 1000) # 343m/s to microseconds
# 343m/s * 100cm/m => 34300cm/s
# 34300cm/s / 1000ms/s => 34,3cm/ms
# 34,3cm/ms / 1000mus/ms => 0,00343 cm/mus

def numMap(value,fromLow,fromHigh,toLow,toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

class mDEV:
    CMD_SERVO1 = 0
    CMD_SERVO2 = 1
    CMD_SERVO3 = 2
    CMD_SERVO4 = 3
    CMD_PWM1 = 4
    CMD_PWM2 = 5
    CMD_DIR1 = 6
    CMD_DIR2 = 7
    CMD_BUZZER = 8
    CMD_IO1 = 9
    CMD_IO2 = 10
    CMD_IO3 = 11
    CMD_SONIC = 12
    SERVO_MAX_PULSE_WIDTH = 2500
    SERVO_MIN_PULSE_WIDTH = 500
    SONIC_MAX_HIGH_BYTE = 100
    Is_IO1_State_True = False
    Is_IO2_State_True = False
    Is_IO3_State_True = False
    Is_Buzzer_State_True = False

    def __init__(self,addr=0x18):
        self.address = addr    #default address of mDEV
        self.bus = smbus.SMBus(1)
        self.bus.open(1)

    def i2c_read(self, reg):
        self.bus.read_byte_data(self.address, reg)

    def i2c_write1(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def i2c_write2(self,value):
        self.bus.write_byte(self.address,value)

    def write_reg(self, reg, value):
        value = int(value)
        try:
            self.bus.write_i2c_block_data(self.address, reg, [value>>8,value&0xff])
            time.sleep(0.001)
            self.bus.write_i2c_block_data(self.address, reg, [value>>8,value&0xff])
            time.sleep(0.001)
            self.bus.write_i2c_block_data(self.address, reg, [value>>8,value&0xff])
            time.sleep(0.001)
        except Exception as e:
            print("I2C Error :",e)

    def read_reg(self, reg):
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

            if a[0] == c and c < self.SONIC_MAX_HIGH_BYTE:
                return c<<8 | d
            else:
                continue
        return 0

    def get_distance(self, samples_to_average=4):
        echo_time = 0.0
        for _ in range(samples_to_average):
            echo_time += mdev.read_reg(mdev.CMD_SONIC)
            time.sleep(0.0005) # 0.5ms

        echo_time /= samples_to_average # echo tme is in mus
        return (echo_time / 2.0) * SPEED_OF_SOUND # divide by 2 for back and forth distance, result is in cm
    
    def set_shield_i2c_address(self,addr): #addr: 7bit I2C Device Address
        if (addr<0x03) or (addr > 0x77) :
            return
        else :
            mdev.write_reg(0xaa,(0xbb<<8)|(addr<<1))

mdev = mDEV()

if __name__ == '__main__':
    import sys
    print("mDev.py is starting ... ")
    #setup()
    try:
        if len(sys.argv)<2:
            print("Parameter error: Please assign the device")
            exit()
        print(sys.argv[0],sys.argv[1])
        if sys.argv[1] == "servo":
            cnt = 3
            while (cnt != 0):
                cnt = cnt - 1
                for i in range(50,140,1):
                    mdev.write_reg(mdev.CMD_SERVO3,numMap(i,0,180,500,2500))
                    time.sleep(0.005)
                for i in range(140,50,-1):
                    mdev.write_reg(mdev.CMD_SERVO3,numMap(i,0,180,500,2500))
                    time.sleep(0.005)
            mdev.write_reg(mdev.CMD_SERVO3,numMap(90,0,180,500,2500))
        if sys.argv[1] == "buzzer":
            mdev.write_reg(mdev.CMD_BUZZER,2000)
            time.sleep(3)
            mdev.write_reg(mdev.CMD_BUZZER,0)
        if sys.argv[1] == "RGBLED":
            for i in range(0,3):
                mdev.write_reg(mdev.CMD_IO1,0)
                mdev.write_reg(mdev.CMD_IO2,1)
                mdev.write_reg(mdev.CMD_IO3,1)
                time.sleep(1)
                mdev.write_reg(mdev.CMD_IO1,1)
                mdev.write_reg(mdev.CMD_IO2,0)
                mdev.write_reg(mdev.CMD_IO3,1)
                time.sleep(1)
                mdev.write_reg(mdev.CMD_IO1,1)
                mdev.write_reg(mdev.CMD_IO2,1)
                mdev.write_reg(mdev.CMD_IO3,0)
                time.sleep(1)
            mdev.write_reg(mdev.CMD_IO1,1)
            mdev.write_reg(mdev.CMD_IO2,1)
            mdev.write_reg(mdev.CMD_IO3,1)
        if sys.argv[1] == "ultrasonic" or sys.argv[1] == "s":
            while True:
                print("Sonic: ",mdev.getSonic())
                time.sleep(0.1)
        if sys.argv[1] == "motor":
                mdev.write_reg(mdev.CMD_DIR1,0)
                mdev.write_reg(mdev.CMD_DIR2,0)
                for i in range(0,1000,10):
                    mdev.write_reg(mdev.CMD_PWM1,i)
                    mdev.write_reg(mdev.CMD_PWM2,i)
                    time.sleep(0.005)
                time.sleep(1)
                for i in range(1000,0,-10):
                    mdev.write_reg(mdev.CMD_PWM1,i)
                    mdev.write_reg(mdev.CMD_PWM2,i)
                    time.sleep(0.005)
                mdev.write_reg(mdev.CMD_DIR1,1)
                mdev.write_reg(mdev.CMD_DIR2,1)
                for i in range(0,1000,10):
                    mdev.write_reg(mdev.CMD_PWM1,i)
                    mdev.write_reg(mdev.CMD_PWM2,i)
                    time.sleep(0.005)
                time.sleep(1)
                for i in range(1000,0,-10):
                    mdev.write_reg(mdev.CMD_PWM1,i)
                    mdev.write_reg(mdev.CMD_PWM2,i)
                    time.sleep(0.005)
    except KeyboardInterrupt:
        pass