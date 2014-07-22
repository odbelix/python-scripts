#!/usr/bin/env python
# 07-2014 Manuel Moscoso Dominguez
########## LIBRERIAS/PAQUETES ##########################################
#PARA LEER
#PARA SALIR por Error
#PARA SLEEP
#PARA LOGS
#PARA FECHA Y HORA
#PARA CONECTAR A MYSQL
#PARA ID PROCESO
########################################################################
import serial
import sys
import time
import syslog
from datetime import datetime
import MySQLdb
import os
########################################################################

########### VARIABLES GLOBALES #########################################
lista_rfid_historicos = []
lista_rfid_unicos = []
host = "localhost"
database = "control_diio" 
username = "root"
password = "1qazxsw2"
tabla = "RFID_LECTURA"
########################################################################

## FUNCION: agregar_rfid_a_tabla
## DESC: Agregar la informacion de lectura a la Base de datos
def agregar_pid_monitor(valor):
	global host
	global username
	global database
	global password
	query = "UPDATE RFID_PARAMETROS SET VALOR = %s WHERE PARAMETRO = 'PID'" % (str(valor))
	db = MySQLdb.connect(host,username,password,database)
	cursor = db.cursor()
	try:
		syslog.syslog(syslog.LOG_INFO, 'PID del Monitor %s' %(str(valor)))
		cursor.execute(query)
		db.commit()
		return True
	except MySQLdb.Error, e:
		syslog.syslog(syslog.LOG_ERR, 'ERROR: %s' % str(e))
		sys.exit("Error MySQLdb: %s" %e)
		return False


## FUNCION: agregar_rfid_a_tabla
## DESC: Agregar la informacion de lectura a la Base de datos
def agregar_rfid_a_tabla(valor):
	global tabla
	global host
	global username
	global database
	global password
	##FECHA,FECHA_MONITOR,BASTON,RFID
	query = "INSERT INTO %s (FECHA,FECHA_MONITOR,BASTON,RFID) VALUES (NOW(),'%s','%s','%s')" % (tabla,valor['FECHA_MONITOR'],valor['BASTON'],valor['RFID'])
	#Execute query	
	db = MySQLdb.connect(host,username,password,database)
	cursor = db.cursor()
	try:
		syslog.syslog(syslog.LOG_INFO, 'Agregando Codigo a la base de datos')
		cursor.execute(query)
		results = cursor.lastrowid
		db.commit()
		syslog.syslog(syslog.LOG_INFO, 'SE AGREGO RFID CON ID: %s' % str(results))
		return results
	except MySQLdb.Error, e:
		syslog.syslog(syslog.LOG_ERR, 'ERROR: %s' % str(e))
		sys.exit("Error MySQLdb: %s" %e)
		return False
	
## FUNCION: valorAhora
## DESC: Obtener el valor de ahora - datetime
def valorAhora():
	datenow = datetime.now()
	return datenow
	
## FUNCION: remove_basura_de_linea
## DESC: Remueve todo tipo de caracteres incesarios en la linea leida
def remove_basura_de_linea(linea):
	syslog.syslog(syslog.LOG_INFO, 'REMOVIENDO BASURA DE RFID')
	codigo = ""
	codigo = linea.replace("\n","")
	codigo = codigo.replace("\r","")
	codigo = codigo.replace("LA ","")
	codigo = codigo.replace("+","")
	return codigo
	
## FUNCION: apertura_puerto
## DESC: Abre un puerto para lectura.
def apertura_puerto(puerto):
	syslog.syslog(syslog.LOG_INFO,'ABRIENDO PUERTO:'+puerto)
	try:
		serial_port = serial.Serial(puerto, 9600, timeout=1) 
	except serial.SerialException as e:
		syslog.syslog(syslog.LOG_ERR,'ERROR PUERTO:'+puerto)
		syslog.syslog(syslog.LOG_ERR,'ERROR:'+str(e))
		sys.exit("ERROR:%s" % e)
	return serial_port

## FUNCION: main
## DESC: Funcion principal que permite la lectura del baston cada 1(s)
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
				
			if "CHL" in linea and len(linea) > 12:
				codigo = remove_basura_de_linea(linea)
				lista_rfid_historicos.append(codigo)
				if codigo not in lista_rfid_unicos:
					syslog.syslog(syslog.LOG_INFO, 'NUEVO RFID:'+codigo)
					lista_rfid_unicos.append(codigo)
					var = {'FECHA_MONITOR':valorAhora(),'BASTON':puerto,'RFID' : codigo }
					agregar_rfid_a_tabla(var)
				else:
					syslog.syslog(syslog.LOG_INFO, 'RFID REPETIDO:'+codigo)
			else:
				syslog.syslog(syslog.LOG_WARNING, 'Linea sin informacion')
			
	ser.close() 
	sio.close()


if __name__ == "__main__":
	
	if len(sys.argv) <> 2:
		sys.exit("Solo se puede recibir como parametro el puerto /dev/PUERTO")
	else:
		agregar_pid_monitor(os.getpid())
		main(sys.argv[1])


