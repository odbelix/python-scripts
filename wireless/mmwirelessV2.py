#!/usr/bin/env python
# 03-2015 Manuel Moscoso Dominguez
########## LIBRERIAS/PAQUETES ##########################################
#PARA CONECTAR A MYSQL
#PARA LOGS
#PARA SALIR
#PARA VERIFICAR EXISTENCIA DE ARCHIVO
#PARA RETARDO DE 20seg
########################################################################
import syslog
import sys
import os.path
from os import listdir
import time
import commands

import rrdtool
from rrdtool import update as rrd_update


import datetime

from pymongo import MongoClient
########################################################################
list_wlc = {'wlc_clients_talca':'192.168.20.135','wlc_clients_curico' : '172.17.1.250','wlc_clients_santaelena' : '172.18.1.250', 'wlc_clients_quebec' : '10.1.1.120'}
#list_wlc = {'wlc_clients_quebec' : '10.1.1.120'}

list_oid_ap = {'AP_NAMES': '1.3.6.1.4.1.14179.2.2.1.1.3','AP_MACAP' : '1.3.6.1.4.1.14179.2.2.1.1.1' , 'AP_MACETH' : '1.3.6.1.4.1.14179.2.2.1.1.33' , 'AP_COUNT': '1.3.6.1.4.1.9.9.618.1.8.4' }
list_oid_client = {'CLIENT_MAC': 'iso.3.6.1.4.1.14179.2.1.4.1.1' , 'CLIENT_IP': 'iso.3.6.1.4.1.14179.2.1.4.1.2', 'CLIENT_MACAP' : 'iso.3.6.1.4.1.14179.2.1.4.1.4' }
list_oid_rogue_ap = { 'AP_ROGUE_NAMES' : 'iso.3.6.1.4.1.14179.2.1.7.1.11' , 'AP_ROGUE_MAC_AP_DET' : 'iso.3.6.1.4.1.14179.2.1.7.1.13', 'AP_ROGUE_LASTREPORT': 'iso.3.6.1.4.1.14179.2.1.7.1.4' }
path_bin = "bash /home/mmoscoso/Documentos/workspace/python-scripts/wireless/mmsnmpV2.sh"


currentDateTime = datetime.datetime.now()


def insertDataOnMongoDB(collection,data_array):
	client = MongoClient('192.168.33.11', 27017)
	db = client['wifimetrics']
	result = db[collection].insert(data_array)
	

def getRogueApInformation(wlcIP):
	global path_bin,list_oid_rogue_ap,currentDateTime
	output1 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_rogue_ap["AP_ROGUE_NAMES"],""))
	output2 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_rogue_ap["AP_ROGUE_MAC_AP_DET"],""))
	output3 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_rogue_ap["AP_ROGUE_LASTREPORT"],""))
	result1 = output1[1].split("\n")
	result2 = output2[1].split("\n")
	result3 = output3[1].split("\n")
	
	result_extra = result2 + result3
	rogue_data = []
	
	rogueApNames = []
	for d in result1:
		if len(d.split(" ")) == 4:
			ROGUENAME = d.split(" ")[3].replace("\"","")
			######## DON'T SAVE AL ROGUE DETECTIONS - DUPLICATE KEY
			if ROGUENAME not in rogueApNames:
				rogueApNames.append(ROGUENAME)
				IDROGUE = d.split(" ")[0].replace(list_oid_rogue_ap["AP_ROGUE_NAMES"],"")
				rogue = {}
				for d1 in result_extra:
					if IDROGUE in d1:
						rogue['NAME'] = ROGUENAME
						rogue['IPWLC'] = wlcIP
						rogue['DATETIME'] = currentDateTime
						if list_oid_rogue_ap["AP_ROGUE_MAC_AP_DET"] in d1.split(" ")[0]:
							rogue['MACAPDET'] = changeMacFormat(d1.split("Hex-STRING:")[1])
						if list_oid_rogue_ap["AP_ROGUE_LASTREPORT"] in d1.split(" ")[0]:
							rogue['LASTREPORT'] = changeMacFormat(d1.split("STRING:")[1])
		
		
				if len(rogue) <> 0:
					rogue_data.append(rogue)
	
			
	#print rogue_data
	#client = MongoClient('192.168.33.11', 27017)
	#db = client['wifimetrics']
	#result = db.rogueap.insert(rogue_data)
	#print result
	insertDataOnMongoDB('rogueap',rogue_data)
		
def getClientInformation(wlcIP):
	global path_bin,list_oid_client,currentDateTime
	
	output1 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_client["CLIENT_IP"],""))
	output2 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_client["CLIENT_MAC"],""))
	output3 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_client["CLIENT_MACAP"],""))
	result1 = output1[1].split("\n")
	result2 = output2[1].split("\n")
	result3 = output3[1].split("\n")
	
	result_extra = result2 + result3
	IDCLIENT = ""
	IPCLIENT = ""

	client_data = []
	for d in result1:
		IPCLIENT = d.split(" ")[3]
		IDCLIENT = d.split(" ")[0].replace(list_oid_client["CLIENT_IP"],"")
		client = {}
		if "0.0.0.0" not in IPCLIENT:
			for d1 in result_extra:
				if IDCLIENT in d1:
					client['IP'] = IPCLIENT
					client['IPWLC'] = wlcIP
					client['DATETIME'] = currentDateTime
					if list_oid_client["CLIENT_MAC"] in d1.split(" ")[0]:
						client['MAC'] = changeMacFormat(d1.split("STRING:")[1])
					if list_oid_client["CLIENT_MACAP"] in d1.split(" ")[0]:
						client['MACAP'] = changeMacFormat(d1.split("Hex-STRING:")[1])
						
		if len(client) <> 0:
			client_data.append(client)
			
	#print client_data
	#client = MongoClient('192.168.33.11', 27017)
	#db = client['wifimetrics']
	#result = db.clients.insert(client_data)
	#print result
	insertDataOnMongoDB('clients',client_data)	
		
def getApInformation(wlcIP):
	global path_bin
	OID = 'iso.3.6.1.4.1.14179.2.2.1.1.3'
	OID_MACAP = '1.3.6.1.4.1.14179.2.2.1.1.1'
	OID_MACET = '1.3.6.1.4.1.14179.2.2.1.1.33'
	output = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,OID,""))
	tempResult = output[1]
	if "\n" in tempResult:
		tempResult = output[1].split("\n")
		i = 1
		ap_data = []
		for result in tempResult:
			ap_array = {}
			data = result.split(" ")
			idAP = data[0].replace(OID,"")
			ap_array['AP_NAME'] = data[3].replace("\"","")
			NEW_OID = OID_MACAP + idAP
			output2 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,NEW_OID,"-Ovq"))
			ap_array['MACAPADDRESS'] = changeMacFormat(output2[1])
			NEW_OID = OID_MACET + idAP
			output3 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,NEW_OID,"-Ovq"))
			ap_array['MACETHADDRESS'] = changeMacFormat(output3[1])
			ap_array['IPWLC'] = wlcIP
			ap_data.append(ap_array)
		
		
		print ap_data
		#client = MongoClient('192.168.33.11', 27017)
		#db = client['wifimetrics']
		#result = db.ap.insert(ap_data)
		#print result
		
		############################################### GET ONE ELEMENT
		#wlcName = db['wlc'].find({"ipaddress": wlcIP})
		#objectMongoDB = wlcName.next()
		#print objectMongoDB["name"]
		################################################################	

def changeMacFormat(macaddress):
	result = macaddress.replace(" ",":")
	result = result.replace("\"","")
	result = result.rstrip(":")
	result = result.lstrip(":")
	result = result.lower()	
	return result

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
				if "MAC" in ObjectName:
					print "%d| %s" % (i,changeMacFormat(result))
				else: 
					print "%d| %s" % (i,result)
				i += 1
		if ObjectName in "CLIENT_IP":
			###### UPDATE RDD  
			print "TOTAL CLIENTES: %d" %(i-1)
			#if  "talca" in wlc:
				##UPDATE RDDFILE
			value = 'N:%d' %(i-1)
			print value
			#ret = rrd_update('/home/mmoscoso/Documentos/workspace/python-scripts/wireless/%s.rrd' %(wlc),value);
			#if ret:
			#	print rrdtool.error()
			#	time.sleep(5)
				
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
				#getApInformation(list_wlc[wlc])
				getClientInformation(list_wlc[wlc])
				getRogueApInformation(list_wlc[wlc])
				#for ObjectName in list_oid_ap:
				#	executeSNMP(wlc,list_wlc[wlc],ObjectName,list_oid_ap[ObjectName]);
				#for ObjectName in list_oid_client:
				#	executeSNMP(wlc,list_wlc[wlc],ObjectName,list_oid_client[ObjectName]);
					
				
				
		time.sleep(1)
		servicio = False
		
if __name__ == "__main__":	
	main()

