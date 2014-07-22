import serial
import syslog
import sys

try:
	serial_port = serial.Serial("/dev/ttyUSB0", 9600, timeout=1) 
except serial.SerialException as e:
	syslog.syslog(syslog.LOG_ERR,'ERROR PUERTO:/dev/ttyUSB0')
	syslog.syslog(syslog.LOG_ERR,'ERROR:'+str(e))
	sys.exit()


if serial_port.isOpen():
	serial_port.flushInput()
	serial_port.flushOutput()
	serial_port.write(b'/x87')
	serial_port.write('0')
	serial_port.write('1')
	serial_port.write(b'/x88')
	serial_port.close()
