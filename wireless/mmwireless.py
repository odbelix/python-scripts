#!/usr/bin/env python
# 03-2015 Manuel Moscoso Dominguez
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
import commands

import rrdtool
from rrdtool import update as rrd_update
########################################################################
list_wlc = {'wlc_clients_talca':'192.168.20.135','wlc_clients_curico' : '172.17.1.250','wlc_clients_santaelena' : '172.18.1.250', 'wlc_clients_quebec' : '10.1.1.120'}
list_oid_ap = {'AP_NAMES': '1.3.6.1.4.1.14179.2.2.1.1.3', 'AP_COUNT': '1.3.6.1.4.1.9.9.618.1.8.4', 'AP_ROGUE_NAMES' : '1.3.6.1.4.1.14179.2.1.7.1.11'}
list_oid_client = {'CLIENT_MAC': '1.3.6.1.4.1.14179.2.1.4.1.1' , 'CLIENT_IP': '1.3.6.1.4.1.14179.2.1.4.1.2'}

path_bin = "bash /home/mmoscoso/Documentos/workspace/python-scripts/wireless/mmsnmp.sh"



## MAC OF 802.11 AP 
##1.3.6.1.4.1.14179.2.1.4.1.4


#https://supportforums.cisco.com/document/9869811/cisco-wlc-snmp-historical-user-statistics-monitoring-w-syslog-or-splunk
#AP_NAMES = "1.3.6.1.4.1.14179.2.2.1.1.3"
#MAC_CLIENTS = "1.3.6.1.4.1.14179.2.1.4.1.1"
#ROGUE_AP_NAMES = "1.3.6.1.4.1.14179.2.1.7.1.11"

#AP_TOTALS = ".1.3.6.1.4.1.9.9.618.1.8.4"
#AP_CLIENTS = ".1.3.6.1.4.1.9.9.618.1.8.12"
#AP_CLIENTS_SECOND = ".1.3.6.1.4.1.14179.2.2.13.1.4"



def executeSNMP(wlc,wlcIP,ObjectName,OID):
	global path_bin
	print "Consultar WLC: %s el OID: %s/ %s" % (wlc,ObjectName,OID)
	output = commands.getstatusoutput(path_bin + ' %s %s' % (wlcIP,OID))
	tempResult = output[1]
	if "\n" in tempResult:
		tempResult = output[1].split("\n")
		i = 1
		for result in tempResult:
			if "0.0.0" not in result: 
				print "%d| %s" % (i,result)
				i += 1
		if ObjectName in "CLIENT_IP":
			###### UPDATE RDD  
			print "TOTAL CLIENTES: %d" %(i-1)
			#if  "talca" in wlc:
				##UPDATE RDDFILE
			value = 'N:%d' %(i-1)
			print value
			ret = rrd_update('/home/mmoscoso/Documentos/workspace/python-scripts/wireless/%s.rrd' %(wlc),value);
			if ret:
				print rrdtool.error()
				time.sleep(5)
				
	else:
		print tempResult
	print "############################################################"

## FUNCION: main
## DESC: Funcion principal que permite lecturas cada X tiempo
def main():
	global list_wlc,list_oid_ap,list_oid_client
	servicio = True
	while servicio == True:
		for wlc in list_wlc:
				for ObjectName in list_oid_ap:
					executeSNMP(wlc,list_wlc[wlc],ObjectName,list_oid_ap[ObjectName]);
				for ObjectName in list_oid_client:
					executeSNMP(wlc,list_wlc[wlc],ObjectName,list_oid_client[ObjectName]);
					
		time.sleep(1)
		servicio = False
		
if __name__ == "__main__":	
	main()

