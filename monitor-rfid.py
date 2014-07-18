#!/usr/bin/env python
# 07-2014 Manuel Moscoso Dominguez
import sys
import os
import os.path
import MySQLdb
import time
import serial

baston = "/dev/rfcomm1"

ser = serial.Serial()
ser.port = baston
ser.baudrate = 9600


ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
    #ser.timeout = None          #block read
ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control

ser.writeTimeout = 2     #timeout for write

try: 
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()



if ser.isOpen():
	try:
		ser.flushInput() #flush input buffer, discarding all its contents
		ser.flushOutput()#flush output buffer, aborting current output 
		#and discard all that is in buffer
		#write data
		ser.write("V")
		ser.write("V")
		ser.write("V")
		ser.write("V")
		print("write data: AT+CSQ")
		time.sleep(0.5)  #give the serial port sometime to receive the data
		numOfLines = 0
		while True:
			response = ser.readline()
			print("read data: " + response)
			numOfLines = numOfLines + 1
			if (numOfLines >= 5):
				break
    
		ser.close()
	##ddexcept: Exception, e1:
	except:
		print "error communicating...: "
else:
	print "cannot open serial port "
