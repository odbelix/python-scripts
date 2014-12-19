#!/usr/bin/env python
# 08-2014 Manuel Moscoso Dominguez
# Vincular GUIAS a la BD
#
########## LIBRERIAS/PAQUETES ##########################################
#PARA CONECTAR A MYSQL
#PARA LOGS
#PARA SALIR
#PARA VERIFICAR EXISTENCIA DE ARCHIVO
#PARA RETARDO DE 20seg
########################################################################
import MySQLdb
import syslog
import sys
import os.path
from os import listdir
import time

########## VARIABLES CONEXION ##########################################
host = "localhost"
database = "control_diio" 
username = "root"
password = "1qazxsw2"
tabla = "ingreso_guia"
tabla_boleto = "ingreso_feria"
########################################################################
continuar_con_archivos = True
#directorio = "/home/PROG2000/EXPORTA/"
directorio = "/home/mmoscoso/Documentos/workspace/python-scripts/"


## FUNCION: obtener_nombre_guia
## DESC: Funcion para consultar el nombre de la guia en el directorio
def obtener_nombre_guia():
	lista = []
	syslog.syslog(syslog.LOG_INFO, 'Verificando archivos en directorio')
	for archivo in listdir(directorio):
		if "csv" in archivo or "CSV" in archivo:
			guia = archivo.replace(".csv","")
			guia = guia.replace(".CSV","")
			lista.append(int(guia))

	return lista

def verificar_guias():
	global host
	global username
	global database
	global password
	global tabla
	
	lista_guias = obtener_nombre_guia()
	query = "SELECT DISTINCT num_guia FROM %s ORDER BY num_guia" % tabla
	db = MySQLdb.connect(host,username,password,database)
	cursor = db.cursor()
	syslog.syslog(syslog.LOG_INFO, 'Verificando valor ultima guia ingresada')
	try:
		cursor.execute(query)
		results = cursor.fetchall()
		for data in results:
			if int(data[0]) in lista_guias:
				lista_guias.remove(data[0])
			syslog.syslog(syslog.LOG_INFO, 'Ultima guia detectada (%s)' % (data[0]))
		
		return sorted(lista_guias)
		
	except MySQLdb.Error, e:
		syslog.syslog(syslog.LOG_ERR, 'ERROR: %s' % str(e))
		sys.exit("Error MySQLdb: %s" %e)
		return False
	
	


## FUNCION: ultima_guia
## DESC: Funcion para consultar la ultima guia en la tabla
def ultima_guia():
	global host
	global username
	global database
	global password
	global tabla
	
	query = "SELECT MAX(num_guia) AS GUIA FROM %s" % tabla
	db = MySQLdb.connect(host,username,password,database)
	cursor = db.cursor()
	syslog.syslog(syslog.LOG_INFO, 'Verificando valor ultima guia ingresada')
	try:
		cursor.execute(query)
		results = cursor.fetchall()
		syslog.syslog(syslog.LOG_INFO, 'Ultima guia detectada (%s)' % (results[0][0]))
		return results[0][0]
	except MySQLdb.Error, e:
		syslog.syslog(syslog.LOG_ERR, 'ERROR: %s' % str(e))
		sys.exit("Error MySQLdb: %s" %e)
		return False


## FUNCION: verificar_boleto
## DESC: Verificar informacion de boleto
def verificar_boleto(valores):
	global host
	global username
	global database
	global password
	global tabla_boleto

	valores = valores.replace("\n","")
	valor = valores.split(";")
	##numeroguia;fecha;boleto;marca;ruporigen;rutorigen;rutdestino
	query = "UPDATE %s SET num_guia = %s ,ruporigen = '%s' ,rutorigen = '%s' ,rutdestino = '%s', rupdestino = '%s',kilos = %s ,precio = %s ,animal = %s WHERE fecha = '%s' and boleto = '%s'" % (tabla_boleto,valor[0],valor[4],valor[5],valor[6],valor[7],valor[8],valor[9],valor[10],valor[1],valor[2])
	
	#Execute query	
	db = MySQLdb.connect(host,username,password,database)
	cursor = db.cursor()
	try:
		syslog.syslog(syslog.LOG_INFO, 'Actualizando guia %s de boleto %s' % (valor[0],valor[2]))
		cursor.execute(query)
		results = cursor.lastrowid
		db.commit()
		return results
	except MySQLdb.Error, e:
		syslog.syslog(syslog.LOG_ERR, 'ERROR: %s' % str(e))
		sys.exit("Error MySQLdb: %s" %e)
		return False
	
## FUNCION: agregar_guia_a_tabla
## DESC: Agregar la informacion de guia a la Base de datos
def agregar_guia_a_tabla(valores):
	global tabla
	global host
	global username
	global database
	global password
	
	valores = valores.replace("\n","")
	valor = valores.split(";")
	##numeroguia;fecha;boleto;marca;ruporigen;rutorigen;rutdestino,KILOS;PRECIO;ANIMAL
	##NUMGUIA;FECHA;BOLETO;MARCA;RUPORIGEN;RUTORIGEN;RUTDESTINO;RUPDESTINO;KILOS;PRECIO;ANIMAL
	query = "INSERT INTO %s (num_guia,fecha,boleto,marca,ruporigen,rutorigen,rutdestino,rupdestino,kilos,precio,animal) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,%s)" % (tabla,valor[0],valor[1],valor[2],valor[3],valor[4],valor[5],valor[6],valor[7],valor[8],valor[9],valor[10])
	#Execute query	
	db = MySQLdb.connect(host,username,password,database)
	cursor = db.cursor()
	try:
		syslog.syslog(syslog.LOG_INFO, 'Agregando guia %s a la base de datos' % (valor[0]))
		cursor.execute(query)
		results = cursor.lastrowid
		db.commit()
		syslog.syslog(syslog.LOG_INFO, 'SE AGREGO RFID CON ID: %s' % str(results))
		return results
	except MySQLdb.Error, e:
		syslog.syslog(syslog.LOG_ERR, 'ERROR: %s' % str(e))
		sys.exit("Error MySQLdb: %s" %e)
		return False

## FUNCION: leer_archivo
## DESC: Funcion para leer el archivo
def leer_archivo(archivo):
	global continuar_con_archivos
	
	syslog.syslog(syslog.LOG_INFO,"Verificando archivo (%s)" % (archivo))
	if os.path.exists(archivo) != True :
		continuar_con_archivos = False
		syslog.syslog(syslog.LOG_INFO,"Archivo (%s) no existe" % (archivo))
		archivo = archivo.replace("csv","CSV")
		if os.path.exists(archivo) != True :
			syslog.syslog(syslog.LOG_INFO,"Archivo (%s) no existe" % (archivo))
			return
			
	archivo = open(archivo,'r')
	lineas = archivo.readlines()
	for linea in lineas:
		agregar_guia_a_tabla(linea)
		verificar_boleto(linea)

	

## FUNCION: main
## DESC: Funcion principal que permite la lectura del baston cada 1(s)
def main():
	global continuar_con_archivos
	
	
	servicio = True
	while servicio == True:
		lista_archivos = verificar_guias()
		for archivo in lista_archivos:
			#nombre_archivo =  str(archivo)+".csv"
			nombre_archivo =  str(archivo)+".CSV"
			leer_archivo(nombre_archivo)
		
		#RETARDO 10 SEG
		time.sleep(15)
		
	#while continuar_con_archivos:
	#	guia = ultima_guia()
	#	if guia == None or guia == 'Null':
	#		syslog.syslog(syslog.LOG_INFO,"No existen ultimas guias en la Tabla")
	#		guia = obtener_nombre_guia()
	#	else:	
	#		guia = guia + 1
	#		
	#	nombre_archivo =  str(guia)+".csv"
	#	leer_archivo(nombre_archivo)
		
		

if __name__ == "__main__":
	
	#if len(sys.argv) <> 2:
	#	sys.exit("Solo se puede recibir como parametro el puerto /dev/PUERTO")
	#else:
	#	verificar_conexion()
	#	agregar_pid_monitor(os.getpid())
	main()

