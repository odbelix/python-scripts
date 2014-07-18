#!/usr/bin/env python
# 07-2014 Manuel Moscoso Dominguez
########## LIBRERIAS/PAQUETES
#PARA LEER
import serial
#PARA SALIR
import sys
#PARA SLEEP
import time
#PARA LOGS
import syslog

## VARIABLES GLOBALES
lista_rfid_historicos = []
lista_rfid_unicos = []



##FUNCION PARA REMOVE BASURA DE LA LINEA
def remove_basura_de_linea(linea):
	syslog.syslog(syslog.LOG_INFO, 'REMOVIENDO BASURA DE RFID')
	codigo = ""
	codigo = linea.replace("\n","")
	codigo = codigo.replace("\r","")
	codigo = codigo.replace("LA ","")
	return codigo
	
##FUNCION PARA LA APERTURA DE PUERTO
def apertura_puerto(puerto):
	syslog.syslog(syslog.LOG_INFO,'ABRIENDO PUERTO:'+puerto)
	try:
		serial_port = serial.Serial(puerto, 9600, timeout=1) 
	except serial.SerialException as e:
		syslog.syslog(syslog.LOG_ERR,'ERROR PUERTO:'+puerto)
		syslog.syslog(syslog.LOG_ERR,'ERROR:'+str(e))
		sys.exit("ERROR:%s" % e)
	
	return serial_port


def main(puerto):
	serial_port = apertura_puerto(puerto)
	
	if serial_port.isOpen():
		serial_port.flushInput()
		serial_port.flushOutput()
		while True:
			time.sleep(1)
			try:
				linea = serial_port.read(serial_port.inWaiting())
			except IOError as io:
				syslog.syslog(syslog.LOG_ERR, 'Perdida de conexion con:'+serial_port.name)
				sys.exit("Perdida de conexion con:"+serial_port.name)
				
			if "CHL" in linea:
				codigo = remove_basura_de_linea(linea)
				lista_rfid_historicos.append(codigo)
				if codigo not in lista_rfid_unicos:
					syslog.syslog(syslog.LOG_INFO, 'NUEVO RFID:'+codigo)
					lista_rfid_unicos.append(codigo)
				
				print lista_rfid_historicos
				print lista_rfid_unicos
			else:
				syslog.syslog(syslog.LOG_WARNING, 'Linea sin informacion')
			
	ser.close() 
	sio.close()


if __name__ == "__main__":
	if len(sys.argv) <> 2:
		sys.exit("Solo se puede recibir como parametro el puerto /dev/PUERTO")
	else: 	
		main(sys.argv[1])


