#!/usr/bin/python3
# coding=utf-8
#
#           bme280.py
#  Read data from a digital pressure sensor.
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#---------------------------------------
from __future__ import print_function
from mq import *
from ky import *
from mics import *
import os
import math
import smbus
import time
import config
import serial, struct, sys, json
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte

DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1
DEVICE = 0x76 # Default device I2C address
light_channel = 1
NH3_channel  = 2
NO2_channel = 3

bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

PORT = '/dev/ttyUSB0'

UNPACK_PAT = '<ccHHHcc'


byte, data = 0, ""

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
    return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
    return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
    result =  data[index] & 0xFF
    return result

def readBME280ID(addr=DEVICE):
  # Chip ID Register Address
    REG_ID     = 0xD0
    (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
    return (chip_id, chip_version)

def readBME280All(addr=DEVICE):
  # Register Addresses
    REG_DATA = 0xF7
    REG_CONTROL = 0xF4
    REG_CONFIG  = 0xF5

    REG_CONTROL_HUM = 0xF2
    REG_HUM_MSB = 0xFD
    REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
    OVERSAMPLE_TEMP = 2
    OVERSAMPLE_PRES = 2
    MODE = 1

  # Oversample setting for humidity register - page 26
    OVERSAMPLE_HUM = 2
    bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

    control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
    bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
    cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
    cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
    cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

    # Convert byte data to word values
    dig_T1 = getUShort(cal1, 0)
    dig_T2 = getShort(cal1, 2)
    dig_T3 = getShort(cal1, 4)

    dig_P1 = getUShort(cal1, 6)
    dig_P2 = getShort(cal1, 8)
    dig_P3 = getShort(cal1, 10)
    dig_P4 = getShort(cal1, 12)
    dig_P5 = getShort(cal1, 14)
    dig_P6 = getShort(cal1, 16)
    dig_P7 = getShort(cal1, 18)
    dig_P8 = getShort(cal1, 20)
    dig_P9 = getShort(cal1, 22)

    dig_H1 = getUChar(cal2, 0)
    dig_H2 = getShort(cal3, 0)
    dig_H3 = getUChar(cal3, 2)

    dig_H4 = getChar(cal3, 3)
    dig_H4 = (dig_H4 << 24) >> 20
    dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

    dig_H5 = getChar(cal3, 5)
    dig_H5 = (dig_H5 << 24) >> 20
    dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

    dig_H6 = getChar(cal3, 6)

    # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
    wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
    time.sleep(wait_time/1000)  # Wait the required time  

    # Read temperature/pressure/humidity
    data = bus.read_i2c_block_data(addr, REG_DATA, 8)
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    #Refine temperature
    var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
    var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
    t_fine = var1+var2
    temperature = float(((t_fine * 5) + 128) >> 8);

    # Refine pressure and adjust for temperature
    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * dig_P6 / 32768.0
    var2 = var2 + var1 * dig_P5 * 2.0
    var2 = var2 / 4.0 + dig_P4 * 65536.0
    var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_P1
    if var1 == 0:
        pressure=0
    else:
        pressure = 1048576.0 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_P9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_P8 / 32768.0
        pressure = pressure + (var1 + var2 + dig_P7) / 16.0

    # Refine humidity
    humidity = t_fine - 76800.0
    humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
    humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
    if humidity > 100:
        humidity = 100
    elif humidity < 0:
        humidity = 0

    return temperature/100.0,pressure/100.0,humidity

def dump(d, prefix=''):
    print(prefix + ' '.join(x.encode('hex') for x in d))

def construct_command(cmd, data=[]):
    assert len(data) <= 12
    data += [0,]*(12-len(data))
    checksum = (sum(data)+cmd-2)%256
    ret = "\xaa\xb4" + chr(cmd)
    ret += ''.join(chr(x) for x in data)
    ret += "\xff\xff" + chr(checksum) + "\xab"

    if DEBUG:
        dump(ret, '> ')
    return ret

def process_data(d):
    r = struct.unpack('<HHxxBB', d[2:])
    pm25 = r[0]/10.0
    pm10 = r[1]/10.0
    checksum = sum(ord(v) for v in d[2:8])%256
    return [pm25, pm10]
    print("PM 2.5: {} µg/m^3  PM 10: {} µg/m^3 CRC={}".format(pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))

def process_version(d):
    r = struct.unpack('<BBBHBB', d[3:])
    checksum = sum(ord(v) for v in d[2:8])%256
    print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]), "OK" if (checksum==r[4] and r[5]==0xab) else "NOK"))

def read_response():
    byte = 0
    while byte != "\xaa":
        byte = ser.read(size=1)

    d = ser.read(size=9)

    if DEBUG:
        dump(d, '< ')
    return byte + d





 # (chip_id, chip_version) = readBME280ID()
 # print "Chip ID     :", chip_id
 # print "Version     :", chip_version

mq = MQ();
#ky = KY();
#mics = MICS();

def all_codes():
 with serial.Serial(PORT, 9600, bytesize=8, parity='N', stopbits=1) as ser:
    while True:
        temperature,pressure,humidity = readBME280All()
        msg = '"D_ID":{},"TS":"{}","TMP":{},"P":{},"H":{},'.format(config.D_ID,time.strftime("%Y-%m-%d %H:%M:%S"),round(temperature,3),round(pressure,3),round(humidity,3))
        

        data = ser.read(10)
        unpacked = struct.unpack(UNPACK_PAT, data)
        pm25 = unpacked[2] / 10.0
        pm10 = unpacked[3] / 10.0
        #print("PM 2.5 = {}, PM 10 = {}".format(pm25, pm10))

        perc = mq.MQPercentage()
        #sys.stdout.write("\r")
        #sys.stdout.write("\033[K")
        #sys.stdout.write("LPG: %g ppm, CO: %g ppm, Smoke: %g ppm" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"]))
        msg = msg+'"LPG":{},"CO":{},"SMK":{},"PM2_5":{},"PM10":{}'.format(round(perc["GAS_LPG"],6),round(perc["CO"],6),round(perc["SMOKE"],6),round(pm25),round(pm10))
        sys.stdout.flush()
        
        #light_level = ky.ReadChannel(light_channel)

        #light_volts = ky.ConvertVolts(light_level,2)
        #msg = msg+',"SND":{},'.format(light_volts)


        #NH3_level =mics.ReadChannel(NH3_channel)
        #NH3_volts=mics.ConvertVolts(NH3_level,2)
        #NO2_level=mics.ReadChannel(NO2_channel)
        #NO2_volts=mics.ConvertVolts(NO2_level,2)


#Ro=2500
        #Ro1=6600
        #Ro2=117000
        #Rs=(1551000-(470000*CO_volts))/CO_volts
        #Rs1=(2350000-(470000*NH3_volts))/NH3_volts
        #Rs2=(50000-(10000*NO2_volts))/NO2_volts


        # x=Rs/Ro
        #x1=Rs1/Ro1
        #x2=Rs2/Ro2

        #CO=4.4638*pow(x,-1.177)
        #NH3=0.6151*pow(x1,-1.903)
        #NO2=0.1516*pow(x2,0.9979)


        
        #msg = msg+'"NH3":{},"NO2":{}'.format(NH3,NO2)
        msg = '{'+msg+'}'
        print(msg)
        return msg
        
        
    
    

all_codes()
