#!/usr/bin/python

import spidev
import time
import os
import math
class MICS():
#Open SPI bus
   def __init__(self, bus = 0, device = 0):
        self.bus, self.device = bus, device
        self.spi = spidev.SpiDev()


        self.spi.open(0,0)
        self.spi.max_speed_hz = 1000000 # 1MHz


#Function to read SPI data from MCP3008 chip
#Channel must be an integer 0-7
   def ReadChannel(self,channel):
        adc = self.spi.xfer2([1,(8+channel)<<4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        return data

#Function to convert data to voltage level,
#rounded to specified number of decimal places.
   def ConvertVolts(self,data,places):
        volts = (data * 3.3) / float(1023)
        volts = round(volts,places)
        return volts


#Function to calculate temperature from
#TMP36 data, rounded to specified
#number of decimal places.
   def ConvertTemp(self,data,places):

#ADC Value
#(approx)  Temp  Volts
#0      -50    0.00
#78      -25    0.25
#155        0    0.50
#233       25    0.75
#310       50    1.00
#465      100    1.50
#775      200    2.50
#1023      280    3.30

        temp = ((data * 330)/float(1023))-50
        temp = round(temp,places)
        return temp

#Define sensor channels
#light_channel = 0
#temp_channel = 1
#CO_channel = 2
   

#Define delay between readings


  