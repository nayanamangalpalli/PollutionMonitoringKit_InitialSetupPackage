#!/usr/bin/python

import spidev

import time

import os

import math
 

class KY():
# Open SPI bus


    def __init__(self, bus = 0, device = 0):
        self.bus, self.device = bus, device
        self.spi = spidev.SpiDev()


        self.spi.open(0,0)
        self.spi.max_speed_hz = 1000000 # 1MHz
            

# Function to read SPI data from MCP3008 chip

# Channel must be an integer 0-7


    def ReadChannel(self,channel):

       adc = self.spi.xfer2([1,(8+channel)<<4,0])
 
       data = ((adc[1]&3) << 8) + adc[2]
  
       return data
 

# Function to convert data to voltage level,

# rounded to specified number of decimal places.


    def ConvertVolts(self,data,places):
  
       volts = (data * 3.3) / float(1023)
  
       volts = round(volts,places)

       if volts!=0:
  
# v2 = -58-20+94+(20*math.log((volts/0.006319),10))
 
#print("sound db",v2)
 
# v3=(0.009*data)+44.87
  
# print("v3:-",v3)
  
          v = (46.74*math.log(data))-238.4+5
 
  #print("log value:")
 
          return v
  
       else:
   
          print("=============================")
 
# print("voltage zero")

          return 70
 

# Function to calculate temperature from

# TMP36 data, rounded to specified

# number of decimal places.

    def ConvertTemp(data,places):

# ADC Value
 
# (approx)  Temp  Volts
 
#    0      -50    0.00
 
#   78      -25    0.25
 
#  155        0    0.50
 
#  233       25    0.75
  
#  310       50    1.00
  
#  465      100    1.50
  
#  775      200    2.50
  
# 1023      280    3.30
 
 
       temp = ((data * 330)/float(1023))-50
  
       temp = round(temp,places)
 
       return temp
 




# Define sensor channels

    
#temp_channel  = 1
 

# Define delay between readings
    


#while True:
 
 
# Read the light sensor data
 
       
# Read the temperature sensor data
 
# temp_level = ReadChannel(temp_channel)
  
# temp_volts = ConvertVolts(temp_level,2)
 
# temp      = ConvertTemp(temp_level,2)
 
 
# Print out results
#  print "--------------------------------------------"
 
#print("Light: {} ({}V)".format(light_level,light_volts))
  
      
# print("NO2 : {} ({}V) deg C".format(temp_level,temp_volts))
 
  
# Wait before repeating loop
  
       
