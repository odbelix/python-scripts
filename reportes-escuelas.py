#!/usr/bin/env python
# 12-2013 Mobiquos	
# mmoscoso@mobiquos.cl
# Generacion automatica de reportes los primero de Cada mes.
# Esto contempla la ejecucion de un CRON como root que hace 5 llamadas al script. 1 por cada Reporte.
import sys
import os
import os.path
import MySQLdb
import time
import datetime
from time import strptime
from datetime import datetime
from datetime import timedelta
#
import pwd
import grp


host = "localhost"
database = "mobmeters" 
username = "root"
password = "1qazxsw2"

#LINARES = 2
isp_id = 2
file_name = ""
path_file = ""


#Execute query
def selectValues(query):
	global host
	global username
	global database
	global password

	db = MySQLdb.connect(host,username,password,database)
	cursor = db.cursor()
	try:
		cursor.execute(query)
		results = cursor.fetchall()
		return results
	except MySQLdb.Error, e:
		print "An error has been passed. %s" %e
		return False
		
		
def newreport(isp_id,day_id,month_id,year,report_id):
	## Report ###############################################################
	## VARIABLES ############################################################
	#Depende del reporte
	
	lista_dias = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miercoles', 'Thursday':'Jueves', 'Friday':'Viernes'}
	global file_name
	global path_file 
	encabezado_archivo = ""
	id_muestra = 1
	respuesta = ""
	contador_fecha = 0
	contador_fecha_anterior = 0
	##NOMBRE ARCHIVO ########################################################
	if report_id == "1":
		file_name = "DETALLE_DISPONIBILIDAD"
		encabezado_archivo = "Id_Muestra\tRBD\tId_Enlace\tAnexo\tEstablecimiento\tTipo_Servicio\tID_BTS\tNombre_BTS\tFecha_Muestra\tDia_Muestra\tHora_Muestra\tDISPONIBILIDAD\tObservacion\n"
		respuesta = respuesta + encabezado_archivo
	elif report_id == "2":
		file_name = "RESUMEN_DISPONIBILIDAD"
	elif report_id == "3":
		file_name = "DETALLE_VEL_CARGA"
		encabezado_archivo = "Id_Muestra\tRBD\tId_Enlace\tAnexo\tEstablecimiento\tTipo_Servicio\tVelocidad\tID_BTS\tNombre_BTS\tFecha_Muestra\tDia_Muestra\tHora_Muestra\tValor_Muestra\tObservacion\n"
		respuesta = respuesta + encabezado_archivo
	elif report_id == "4":
		file_name = "DETALLE_VEL_DESCARGA"
		encabezado_archivo = "Id_Muestra\tRBD\tId_Enlace\tAnexo\tEstablecimiento\tTipo_Servicio\tVelocidad\tID_BTS\tNombre_BTS\tFecha_Muestra\tDia_Muestra\tHora_Muestra\tValor_Muestra\tObservacion\n"
		respuesta = respuesta + encabezado_archivo
	else:
		file_name = "RESUMEN_VELOCIDAD"
	########################################################################

	
	##CREACION DE RESPUESTA - DESCARGA DE ARCHIVO ##########################
	#Place
	# SELECT * FROM bw_place WHERE availability = 1 and isp = %s ORDER BY RBD"
    ##
	query = "SELECT rbd,name,ipaddress,bwdown,bwup FROM stats_place WHERE availability = 1 and isp_id = %s ORDER BY rbd" % isp_id
	resultados_place = selectValues(query)

	for escuela in resultados_place:
		#VARIABLES PARA REPORTE DE RESUMEN MEDICIONES
		list_bwup = {}
		list_bwdown = {}
		list_day_speed = []
		list_av = {}
		if report_id == "2" or report_id == "5":
			if contador_fecha > contador_fecha_anterior:
				contador_fecha_anterior = 0
				contador_fecha_anterior = contador_fecha
				contador_fecha = 0

		if report_id == "2":
			linea = str(escuela[0])+"\t0\t"+str(escuela[1])+"\t"+"RF\t"
			respuesta = respuesta + linea

		if report_id == "5":
			linea = str(escuela[0])+"\t0\t"+str(escuela[1])+"\t"+"RF\t"
			linea = linea + escuela[3] + "\t" + escuela[4] + "\t" + "20/01/2012\t12:00\t"

			#respuesta = respuesta + linea

		#RECORRER LAS FECHAS HASTA LA SELECCIONADA
		fecha_inicio = 1
		for dia in range(fecha_inicio,int(day_id)+1):
			#VALIDAR SI dia es LUNES-VIERNES
			nombre_dia_fecha = datetime.strptime('%s%s%s' % (str(dia).zfill(2),str(month_id),str(year)), '%d%m%Y').date()
			nombre_dia = str(nombre_dia_fecha.strftime('%A'))
			if nombre_dia in lista_dias.keys():
				#LINEA CON INFORMACION
				#linea = ""
				#DETALLE_DISPONIBLIDAD
				if report_id ==  "1":	
					#LINEA CON INFORMACION
					linea = ""
					#DISPONIBILIDAD
					#DD/MM/YYYY DIA HH:MM:SS VALOR_DISPONIBILIDAD
					#DIA valor.datereg.strftime('%A')
                	#HORA valor.datereg.strfime('%H:%M:%S')	
					query_availability = "SELECT date,datereg,value FROM stats_availability WHERE ipplace = '%s' AND date_format(datereg,'%%d-%%m-%%Y') = '%s-%s-%s' ORDER BY datereg " %(escuela[2],str(dia).zfill(2),month_id,year)
					results_availability = selectValues(query_availability);
					
					#SI EXISTEN VALORES PARA DISPONIBILIDAD
					if len(results_availability) <> 0:
						for d in results_availability:
							#VALIDAR HORA DE LA MEDICION
							horario_medida = datetime.strptime('%s' % (d[0]),'/%d/%m/%Y/ - %H:%M:%S').date()
							horario_medida = datetime(*strptime(d[0],"/%d/%m/%Y/ - %H:%M:%S")[0:6])
							hora_medida = int(horario_medida.strftime('%H'))
							if hora_medida > 8 and hora_medida < 19:
								#VALOR CORRECTO, AGREGAR AL ARCHIVO
								linea = str(id_muestra)+"\t"+str(escuela[0])+"\t0\t0\t"+str(escuela[1])+"\t"+"Radioenlace"
								respuesta = respuesta+linea+"\t"+"%s/%s/%s\t" %(str(str(dia).zfill(2)),str(month_id),str(year))
								respuesta = respuesta+lista_dias[d[1].strftime('%A')]+"\t"
								respuesta = respuesta+d[1].strftime('%H:%M:%S')+"\t"
								respuesta = respuesta+str(d[2])+"\n"
								id_muestra = id_muestra + 1


				#RESUMEN DISPONIBILIDAD
				if report_id == "2":
					suma_disp = 0
					contador_disp = 0
					promedio_disp = 0
					query_availability = "SELECT date,datereg,value FROM stats_availability WHERE ipplace = '%s' AND date_format(datereg,'%%d-%%m-%%Y') = '%s-%s-%s' ORDER BY datereg " %(escuela[2],str(dia).zfill(2),month_id,year)
					results_availability = selectValues(query_availability);
					
					#SI EXISTEN VALORES PARA DISPONIBILIDAD
					if len(results_availability) <> 0:
						contador_disp = 0
						for d in results_availability:
							#VALIDAR HORA DE LA MEDICION
							horario_medida = datetime.strptime('%s' % (d[0]),'/%d/%m/%Y/ - %H:%M:%S').date()
							horario_medida = datetime(*strptime(d[0],"/%d/%m/%Y/ - %H:%M:%S")[0:6])
							hora_medida = int(horario_medida.strftime('%H'))
							if hora_medida > 8 and hora_medida < 19:
								#VALOR CORRECTO, AGREGAR AL ARCHIVO
								suma_disp = suma_disp + int(d[2])
								contador_disp = contador_disp + 1
								
						if contador_disp <> 0:
							promedio_disp = int(suma_disp)/int(contador_disp)
							respuesta = respuesta + d[1].strftime("/%d/%m/%Y/")+"\t"+str(promedio_disp)+"\t"
							list_av.update({datetime(int(year),int(month_id),int(dia)).strftime("%d/%m/%Y"):promedio_disp})
						
						#contador_fecha = contador_fecha + 1
				
				#DETALLE VELOCIDADES				
				if report_id ==  "3" or report_id ==  "4":
					#LINEA CON INFORMACION
					linea = ""
					#VELOCIDAD
					#VALOR_VELOCIDAD DD/MM/YYYY DIA HH:MM:SS VALOR_VELOCIDAD
					#DIA valor.datereg.strftime('%A')
					#HORA valor.datereg.strfime('%H:%M:%S')
					# DIFERECIAR ENTRE CARGA Y DESCARGA
					if report_id == "3":
						#BWUP
						query_bwdata = "SELECT date,datereg,bw FROM stats_bwup WHERE ipdst = '%s' AND date_format(datereg,'%%d-%%m-%%Y') = '%s-%s-%s' ORDER BY datereg " %(escuela[2],str(dia).zfill(2),month_id,year)
						#bwdata = Bwup.objects.filter(ipdst=escuela.ipaddress,
						#	datereg__day=dia,datereg__month=month_id,datereg__year=year).order_by('datereg')
						velocidad = escuela[4]
					else:
						query_bwdata = "SELECT date,datereg,bw FROM stats_bwdown WHERE ipsrc = '%s' AND date_format(datereg,'%%d-%%m-%%Y') = '%s-%s-%s' ORDER BY datereg " %(escuela[2],str(dia).zfill(2),month_id,year)
						#bwdata = Bwdown.objects.filter(ipsrc=escuela.ipaddress,
                         #                               datereg__day=dia,datereg__month=month_id,datereg__year=year).order_by('datereg')
						velocidad = escuela[3]
				
					
					results_bwdata = selectValues(query_bwdata)
					#SI EXISTEN VALORES PARA VELOCIDAD
					if len(results_bwdata) <> 0:
						for bw in results_bwdata:
							#VALIDAR HORA DE LA MEDICION
							horario_medida = datetime.strptime('%s' % (bw[0]),'/%d/%m/%Y/ - %H:%M:%S').date()
							horario_medida = datetime(*strptime(bw[0],"/%d/%m/%Y/ - %H:%M:%S")[0:6])
							hora_medida = int(horario_medida.strftime('%H'))
							if hora_medida > 8 and hora_medida < 19:
								#VALOR CORRECTO, AGREGAR AL ARCHIVO
								linea = str(id_muestra)+"\t"+str(escuela[0])+"\t0\t0\t"+str(escuela[1])+"\t"+"Radioenlace\t"+velocidad
								respuesta = respuesta+linea+"\t"+"%s/%s/%s\t" %(str(str(dia).zfill(2)),str(month_id),str(year))
								respuesta = respuesta+lista_dias[bw[1].strftime('%A')]+"\t"
								respuesta = respuesta+bw[1].strftime('%H:%M:%S')+"\t"
								kilobits = "%.2f" % (float(bw[2])/1024)
								respuesta = respuesta+str(kilobits)+"\n"
								id_muestra = id_muestra + 1

				if report_id == "5":
					suma_bwup = 0
					contador_bwup = 0
					promedio_bwup = 0
					
					query_bwupdata = "SELECT date,datereg,bw FROM stats_bwup WHERE ipdst = '%s' AND date_format(datereg,'%%d-%%m-%%Y') = '%s-%s-%s' ORDER BY datereg " %(escuela[2],str(dia).zfill(2),month_id,year)
					query_bwdowndata = "SELECT date,datereg,bw FROM stats_bwdown WHERE ipdst = '%s' AND date_format(datereg,'%%d-%%m-%%Y') = '%s-%s-%s' ORDER BY datereg " %(escuela[2],str(dia).zfill(2),month_id,year)
					
					results_bwup = selectValues(query_bwupdata)
					results_bwdown = selectValues(query_bwdowndata)
					
					
					#SI EXISTEN VALORES PARA DISPONIBILIDAD
					if len(results_bwup) <> 0:
						contador_bwup = 0
						for bw in results_bwup:
							#VALIDAR HORA DE LA MEDICION
							horario_medida = datetime.strptime('%s' % (bw[0]),'/%d/%m/%Y/ - %H:%M:%S').date()
							horario_medida = datetime(*strptime(bw[0],"/%d/%m/%Y/ - %H:%M:%S")[0:6])
							hora_medida = int(horario_medida.strftime('%H'))
							if hora_medida > 8 and hora_medida < 19:
								#VALOR CORRECTO, AGREGAR AL ARCHIVO
								suma_bwup = suma_bwup + float(bw[2])
								contador_bwup = contador_bwup + 1
								if contador_bwup <> 0:
									promedio_bwup = "%.2f " % float((suma_bwup)/contador_bwup)
									promedio_kilobits = "%.2f " % float(float(promedio_bwup)/1024)
									list_bwup.update({datetime(int(year),int(month_id),int(dia)).strftime("%d/%m/%Y"):promedio_kilobits})
									contador_fecha = contador_fecha + 1
									
									if datetime(int(year),int(month_id),int(dia)).strftime("%d/%m/%Y")  not in list_day_speed:
										list_day_speed.append(datetime(int(year),int(month_id),int(dia)).strftime("%d/%m/%Y"))
										
								
						
								
					
					
					if len(results_bwdown) <> 0:
						contador_bwdown = 0
						suma_bwdown = 0
						contador_bwdown = 0
						
						for bw in results_bwdown:
							#VALIDAR HORA DE LA MEDICION
							horario_medida = datetime.strptime('%s' % (bw[0]),'/%d/%m/%Y/ - %H:%M:%S').date()
							horario_medida = datetime(*strptime(bw[0],"/%d/%m/%Y/ - %H:%M:%S")[0:6])
							hora_medida = int(horario_medida.strftime('%H'))
							
							if hora_medida > 8 and hora_medida < 19:
								#VALOR CORRECTO, AGREGAR AL ARCHIVO
								suma_bwdown = suma_bwdown + float(bw[2])
								contador_bwdown = contador_bwdown + 1
								
								if contador_bwdown <> 0:
									promedio_bwdown = "%.2f " % float((suma_bwdown)/contador_bwdown)
									promedio_kilobits = "%.2f " % float(float(promedio_bwdown)/1024)
									list_bwdown.update({datetime(int(year),int(month_id),int(dia)).strftime("%d/%m/%Y"):promedio_kilobits})
									
									if datetime(int(year),int(month_id),int(dia)).strftime("%d/%m/%Y")  not in list_day_speed:
										list_day_speed.append(datetime(int(year),int(month_id),int(dia)).strftime("%d/%m/%Y"))


				#FIN if report_id == "5":

		#SALTO DE LINEA PARA RESUMENES
		if report_id == "2":
			print "%d list_av" % (len(list_av))
			print "%d < %d " % (contador_fecha,contador_fecha_anterior)
			respuesta = respuesta + "\n"
		if report_id == "5":
			contador_fecha = len(list_bwup)
			if contador_fecha < len(list_bwdown):
				contador_fecha = len(list_bwdown)
		
			respuesta = respuesta + linea
			for k in list_day_speed:
				respuesta = respuesta + str(k).replace(" ","")+ "\t" 
				if k in list_bwdown:
					respuesta = respuesta + str(list_bwdown[k]).replace(" ","")+ "\t"
				else:
					respuesta = respuesta + str(0) + "\t"
				
				if k in list_bwup:
					respuesta = respuesta + str(list_bwup[k]).replace(" ","") + "\t"
				else:
					respuesta = respuesta + str(0) + "\t"
				#respuesta = respuesta + str(k).replace(" ","") + "\t" + str(list_bwdown[k]).replace(" ","") + "\t" + str(list_bwup[k]).replace(" ","") + "\t"
			respuesta = respuesta + "\n"
	
	#COMPLETAR ENCABEZADO DE REPORTES
	if report_id == "2":
		print "%d < %d" % (contador_fecha,contador_fecha_anterior)
		if contador_fecha < contador_fecha_anterior:
			contador_fecha = contador_fecha_anterior
		texto_fecha = ""
		for i in range(1,contador_fecha+1):
			texto_fecha = texto_fecha + "fecha_%s\tdisp_%s\t" % (str(i),str(i))
		respuesta = "RBD\tANEXO\tESTABLECIMINENTO\tTIPO_SERVICIO\t" +texto_fecha +"\n" + respuesta

	if report_id == "5":
		if contador_fecha < contador_fecha_anterior:
			contador_fecha = contador_fecha_anterior
		
		texto_fecha = ""
		for i in range(1,contador_fecha+1):
			texto_fecha = texto_fecha + "fecha_%s\tvel_bajada_%s\tvel_subida_%s\t" % (str(i),str(i),str(i))
				
		respuesta = "RBD\tANEXO\tESTABLECIMINENTO\tTIPO_SERVICIO\tID_BTS\tNOMBRE_BRS\tVEL_BAJADA\tVEL_SUBIDA\tFECHA_ALTA\tHORA_ALTA\t" +texto_fecha +"\n" + respuesta
	########################################################################
    
	path = '%s%s_%s_%s_%s.txt' % (path_file,year,month_id,day_id,file_name)
	file_report = open(path ,'w')
	file_report.write(respuesta)
	file_report.close()
	##CHANGE PRIVILEGES
	uid = pwd.getpwnam("www-data").pw_uid
	gid = grp.getgrnam("www-data").gr_gid
	
	os.chown(path, uid, gid)
	
	return True



def main():
	global isp_id
		
	#Get current date and Check if first of month
	datenow = datetime.now()
	datenow = datetime(2013,12,1)
	
	
	if not datenow.day == 1:
		sys.exit("Alert!: It's not a day(%s) to do Reports :D" % (datenow.strftime('%Y-%m-%d')))

	if len(sys.argv) <> 2:
		sys.exit("Alert!: Not enogth arguments to do Reports :D")
	else:
		if int(sys.argv[1]) not in [1,2,3,4,5]:
				sys.exit("Alert!: Report ID invalid:\n1)\t \n2)\t \n3)\t \n4)\t \n5)\n \n")
		else:
			report_id = str(sys.argv[1])
	
	#
	#Creating report
	#
	lastday = (datenow + timedelta(hours=-24))
	year = lastday.strftime('%Y');
	month = lastday.strftime('%m');
	day = lastday.strftime('%d');
	
	
	text_report = newreport(isp_id,day,month,year,report_id)
	
		
		
		
if __name__ == "__main__":
    main()
    
    
