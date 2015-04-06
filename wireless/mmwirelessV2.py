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
import sys, os
#from os import listdir
import time
import commands
#import rrdtool
#Just Update DB
from rrdtool import update as rrd_update 
import datetime
from pymongo import MongoClient
########################################################################
list_wlc = {'wlc_clients_talca':'192.168.20.135','wlc_clients_curico' : '172.17.1.250','wlc_clients_santaelena' : '172.18.1.250', 'wlc_clients_quebec' : '10.1.1.120'}
list_oid_ap = {'AP_NAMES': '1.3.6.1.4.1.14179.2.2.1.1.3','AP_MACAP' : '1.3.6.1.4.1.14179.2.2.1.1.1' , 'AP_MACETH' : '1.3.6.1.4.1.14179.2.2.1.1.33' , 'AP_COUNT': '1.3.6.1.4.1.9.9.618.1.8.4' }
list_oid_client = {'CLIENT_MAC': 'iso.3.6.1.4.1.14179.2.1.4.1.1' , 'CLIENT_IP': 'iso.3.6.1.4.1.14179.2.1.4.1.2', 'CLIENT_MACAP' : 'iso.3.6.1.4.1.14179.2.1.4.1.4' }
list_oid_rogue_ap = { 'AP_ROGUE_NAMES' : 'iso.3.6.1.4.1.14179.2.1.7.1.11' , 'AP_ROGUE_MAC_AP_DET' : 'iso.3.6.1.4.1.14179.2.1.7.1.13', 'AP_ROGUE_LASTREPORT': 'iso.3.6.1.4.1.14179.2.1.7.1.4' }

SNMP_SCRIPT_NAME = "mmsnmpV2.sh"
path_bin = "bash " + os.path.dirname(sys.argv[0]) + "/" + SNMP_SCRIPT_NAME
#path_rrddb = "/home/mmoscoso/Documentos/workspace/python-scripts/wireless"
#path_snmp_logs = "/home/mmoscoso/Documentos/workspace/python-scripts/wireless/logs"
path_rrddb = "/home/plataforma"
path_snmp_logs = "/home/plataforma/logs"
log_name = "LOG_SNMP_"
########################################################################
# Summaries collections 
clientsCount = []
clientCollection = 'clientsummary'
apCount = []
apCollection = 'apsummary'
summaryCollection = 'summary'
########################################################################
# Time Start/End Measure 
startSummary = datetime.datetime.now()
startMeasure = datetime.datetime.now()
endMeasure = datetime.datetime.now()
########################################################################
# Output Variables for SNMP queries results
output_snmp_rogueap_names = ""
output_snmp_rogueap_macdet = ""
output_snmp_rogueap_lastreport = ""
output_snmp_clients_ip = ""
output_snmp_clients_mac = ""
output_snmp_clients_macap = ""
########################################################################
# Log collections and actions
logs = []
logCollection = 'log'
logActionStartMeasuring = 'Start measuring'
logActionStopMeasuring = 'Stop measuring'
logActionStartClients = 'Start proccessing clients measures'
logActionStopClients = 'Stop proccessing clients measures'
logActionStartRogue = 'Start proccessing RogueAP measures'
logActionStopRogue = 'Stop proccessing RogueAP measures'
logActionStartAp = 'Start proccessing AP measures'
logActionStopAp = 'Stop proccessing AP measures'
########################################################################
# MongoDB parameters
ipMongoDB = '192.168.33.11'
nameDBMongo = 'wifimetrics'
########################################################################
def clearingAllList():
	global clientsCount,apCount,logs
	clientsCount = []
	apCount = []
	logs = []
	

def setDatetimeMeasure():
	global startSummary,startMeasure,endMeasure
	startSummary = datetime.datetime.now()
	startMeasure = datetime.datetime.now()
	endMeasure = datetime.datetime.now()
	
	
def creatingSNMPLogFile(NAMEOUTPUT,OUTPUT,WLCIP):
	global log_name,path_snmp_logs,startSummary
	syslog.syslog(syslog.LOG_INFO,"(" + WLCIP + ") Adding content of %s to log_snmp" % (NAMEOUTPUT) )
	message = "#####################################################\n"
	message = message + "(" + WLCIP + "):" + NAMEOUTPUT + "\n"
	message = message + OUTPUT[1]
	message = message + "\n#####################################################\n"
	file_path = path_snmp_logs + "/" + log_name + startSummary.strftime("%Y%m%d_%H%M")
	file_object = open(file_path,"a")
	file_object.write(message)
	syslog.syslog(syslog.LOG_INFO,"(" + WLCIP + ") Finish-Adding content of %s to log_snmp" % (NAMEOUTPUT) )
##
def addingLog(DATETIME,ACTION,WLCIP):
	global logs
	syslog.syslog(syslog.LOG_INFO,"(" + WLCIP + ") " +ACTION + " (" + DATETIME.strftime("%Y-%m-%d %H:%M:%S") + ")")
	log = {}
	log['DATETIME'] = datetime.datetime.now()
	log['DATETIMEEXE'] = DATETIME
	log['ACTION'] = ACTION + ' : ' + WLCIP
	log['IPWLC'] = WLCIP
	logs.append(log)

##
def savingLogs():
	global logs,logCollection
	insertDataOnMongoDB(logCollection,logs,"LOGs")

def updateRRDFile(wlc,nClients):
	global path_rrddb
	value = 'N:%d' % (nClients)
	ret = rrd_update( path_rrddb +'/%s.rrd' %(wlc),value);
	if ret:
		print rrdtool.error()
	
##
def logOutputLen(WLCIP):
	global output_snmp_rogueap_names,output_snmp_rogueap_macdet
	global output_snmp_rogueap_lastreport
	global output_snmp_clients_ip,output_snmp_clients_mac,output_snmp_clients_macap
	
	syslog.syslog(syslog.LOG_INFO,"(%s) output_snmp_rogueap_names LEN(%d)" % (WLCIP,len(output_snmp_rogueap_names[1])))
	syslog.syslog(syslog.LOG_INFO,"(%s) output_snmp_rogueap_macdet LEN(%d)" % (WLCIP,len(output_snmp_rogueap_macdet[1])))
	syslog.syslog(syslog.LOG_INFO,"(%s) output_snmp_rogueap_lastreport LEN(%d)" % (WLCIP,len(output_snmp_rogueap_lastreport[1])))
	syslog.syslog(syslog.LOG_INFO,"(%s) output_snmp_clients_ip LEN(%d)" % (WLCIP,len(output_snmp_clients_ip[1])))
	syslog.syslog(syslog.LOG_INFO,"(%s) output_snmp_clients_mac LEN(%d)" % (WLCIP,len(output_snmp_clients_mac[1])))
	syslog.syslog(syslog.LOG_INFO,"(%s) output_snmp_clients_macap LEN(%d)" % (WLCIP,len(output_snmp_clients_macap[1])))
	
##
def getInformationBySNMP(wlcIP):
	global path_bin
	global startMeasure,endMeasure
	global output_snmp_rogueap_names,output_snmp_rogueap_macdet
	global output_snmp_rogueap_lastreport
	global output_snmp_clients_ip,output_snmp_clients_mac,output_snmp_clients_macap
	global logCollection,logActionStartMeasuring,logActionStopMeasuring
	global logs
	
	startMeasure = datetime.datetime.now()
	## LOG
	addingLog(startMeasure,logActionStartMeasuring,wlcIP)

	# MEASURING
	output_snmp_clients_ip = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_client["CLIENT_IP"],""))
	creatingSNMPLogFile("output_snmp_clients_ip",output_snmp_clients_ip,wlcIP)
	
	output_snmp_clients_mac = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_client["CLIENT_MAC"],""))
	creatingSNMPLogFile("output_snmp_clients_mac",output_snmp_clients_mac,wlcIP)
	
	output_snmp_clients_macap = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_client["CLIENT_MACAP"],""))
	creatingSNMPLogFile("output_snmp_clients_macap",output_snmp_clients_macap,wlcIP)
	
	output_snmp_rogueap_names = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_rogue_ap["AP_ROGUE_NAMES"],""))
	creatingSNMPLogFile("output_snmp_rogueap_names",output_snmp_rogueap_names,wlcIP)
	
	output_snmp_rogueap_macdet = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_rogue_ap["AP_ROGUE_MAC_AP_DET"],""))
	creatingSNMPLogFile("output_snmp_rogueap_macdet",output_snmp_rogueap_macdet,wlcIP)
	
	output_snmp_rogueap_lastreport = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,list_oid_rogue_ap["AP_ROGUE_LASTREPORT"],""))
	creatingSNMPLogFile("output_snmp_rogueap_lastreport",output_snmp_rogueap_lastreport,wlcIP)
	
	endMeasure = datetime.datetime.now()
	## LOG
	logOutputLen(wlcIP)
	addingLog(endMeasure,logActionStopMeasuring,wlcIP)
	
	
## Insert Data on MongoDB	
def insertDataOnMongoDB(collection,data_array,WLCIP):
	global ipMongoDB,nameDBMongo
	if ( len(data_array) > 0 ):
		client = MongoClient(ipMongoDB, 27017)
		db = client[nameDBMongo]
		result = db[collection].insert(data_array)
		message = "Store %d record in %s from %s" % ( len(result) , collection , WLCIP )
		addingLog(datetime.datetime.now(),message,WLCIP)
	else:
		message = "Not enough elements for store in collection %s from %s " % (collection , WLCIP )
	
## Data of RogueAP
def getRogueApInformation(wlcIP):
	global path_bin,list_oid_rogue_ap,startMeasure
	global output_snmp_rogueap_names,output_snmp_rogueap_macdet
	global output_snmp_rogueap_lastreport
	## LOG
	global logActionStartRogue,logActionStopRogue
	addingLog(datetime.datetime.now(),logActionStartRogue,wlcIP)
	
	result1 = output_snmp_rogueap_names[1].split("\n")
	result2 = output_snmp_rogueap_macdet[1].split("\n")
	result3 = output_snmp_rogueap_lastreport[1].split("\n")
	
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
						rogue['DATETIME'] = startMeasure
						if list_oid_rogue_ap["AP_ROGUE_MAC_AP_DET"] in d1.split(" ")[0]:
							rogue['MACAPDET'] = changeMacFormat(d1.split("Hex-STRING:")[1])
						if list_oid_rogue_ap["AP_ROGUE_LASTREPORT"] in d1.split(" ")[0]:
							rogue['LASTREPORT'] = changeMacFormat(d1.split("STRING:")[1])
				if len(rogue) <> 0:
					rogue_data.append(rogue)
					
	insertDataOnMongoDB('rogueap',rogue_data,wlcIP)
	addingLog(datetime.datetime.now(),logActionStopRogue,wlcIP)

## Data of Clients		
def getClientInformation(wlcIP,wlc):
	global clientsCount
	global path_bin,list_oid_client,startMeasure
	global output_snmp_clients_ip,output_snmp_clients_mac,output_snmp_clients_macap
	## LOG
	global logActionStartClients,logActionStopClients
	addingLog(datetime.datetime.now(),logActionStartClients,wlcIP)
	
	result1 = output_snmp_clients_ip[1].split("\n")
	result2 = output_snmp_clients_mac[1].split("\n")
	result3 = output_snmp_clients_macap[1].split("\n")
	
	result_extra = result2 + result3
	IDCLIENT = ""
	IPCLIENT = ""

	client_data = []
	aps = {}
	if "OID" not in output_snmp_clients_ip[1]:
		for d in result1:
			IPCLIENT = d.split(" ")[3]
			IDCLIENT = d.split(" ")[0].replace(list_oid_client["CLIENT_IP"],"")
			client = {}
			if "0.0.0.0" not in IPCLIENT:
				for d1 in result_extra:
					if IDCLIENT in d1:
						client['IP'] = IPCLIENT
						client['IPWLC'] = wlcIP
						client['DATETIME'] = startMeasure
						if list_oid_client["CLIENT_MAC"] in d1.split(" ")[0]:
							client['MAC'] = changeMacFormat(d1.split("STRING:")[1])
						if list_oid_client["CLIENT_MACAP"] in d1.split(" ")[0]:
							client['MACAP'] = changeMacFormat(d1.split("Hex-STRING:")[1])
							if client['MACAP'] in aps.keys():
								aps[client['MACAP']] += 1
							else:
								aps[client['MACAP']] = 1
							
			if len(client) <> 0:
				client_data.append(client)
	else:
		syslog.syslog(syslog.LOG_INFO,output_snmp_clients_ip[1])
	
	insertDataOnMongoDB('clients',client_data,wlcIP)
	updateRRDFile(wlc,len(client_data))
	addingClientSummary(wlc,wlcIP,len(client_data))
	addingApCountSummary(wlc,wlcIP,aps)
	addingLog(datetime.datetime.now(),logActionStopClients,wlcIP)

##
def addingApCountSummary(WLC,WLCIP,APS):
	global apCount,startMeasure
	for d in APS:
		apDetail = {}
		apDetail['DATETIME'] = startMeasure
		apDetail['IPWLC'] = WLCIP
		apDetail['NAMEWLC'] = WLC
		apDetail['MACAP'] = d
		apDetail['CLIENTS'] = APS[d]
		apCount.append(apDetail)
	
##
def addingClientSummary(WLC,WLCIP,CLIENTCOUNT):
	global clientsCount,startMeasure
	clientNumber = {}
	clientNumber['DATETIME'] = startMeasure
	clientNumber['IPWLC'] = WLCIP
	clientNumber['NAMEWLC'] = WLC
	clientNumber['CLIENTS'] = CLIENTCOUNT
	clientsCount.append(clientNumber)


## Saving Summary
def savingSummary():
	global summaryCollection,startSummary,endMeasure
	global ipMongoDB,nameDBMongo
	summries = []
	summary = {}
	client = MongoClient(ipMongoDB, 27017)
	db = client[nameDBMongo]
	result = db[summaryCollection].find().count()
	summary['DATETIMESTART'] = startSummary
	summary['DATETIMESTOP'] = endMeasure
	summary['NUMBER'] = result + 1
	summries.append(summary)
	insertDataOnMongoDB(summaryCollection,summries,"savingSummary")

## Saving Client Summary
def savingClientSummary():
	global clientsCount,clientCollection
	insertDataOnMongoDB(clientCollection,clientsCount,"savingClientSummary")
	
## Saving Ap Summary
def savingApSummary():
	global apCount,apCollection
	insertDataOnMongoDB(apCollection,apCount,"ApSummary")	
		
## Data of AP
def getApInformation(wlcIP):
	global path_bin
	OID = 'iso.3.6.1.4.1.14179.2.2.1.1.3'
	OID_MACAP = 'iso.3.6.1.4.1.14179.2.2.1.1.1'
	OID_MACET = 'iso.3.6.1.4.1.14179.2.2.1.1.33'
	global logActionStartAp,logActionStopAp
	
	addingLog(datetime.datetime.now(),logActionStartAp,wlcIP)
	
	output = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,OID,""))
	tempResult = output[1]
	if "\n" in tempResult:
		tempResult = output[1].split("\n")
		i = 1
		ap_data = []
		for result in tempResult:
			ap = {}
			data = result.split(" ")
			idAP = data[0].replace(OID,"")
			ap['AP_NAME'] = data[3].replace("\"","")
			NEW_OID = OID_MACAP + idAP
			output2 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,NEW_OID,"-Ovq"))
			ap['MACAPADDRESS'] = changeMacFormat(output2[1])
			NEW_OID = OID_MACET + idAP
			output3 = commands.getstatusoutput(path_bin + ' %s %s %s' % (wlcIP,NEW_OID,"-Ovq"))
			ap['MACETHADDRESS'] = changeMacFormat(output3[1])
			ap['IPWLC'] = wlcIP
			ap_data.append(ap)
		
		
		#print ap_data
	insertDataOnMongoDB('ap',ap_data,wlcIP)
	addingLog(datetime.datetime.now(),logActionStopAp,wlcIP)

## Change format of Mac, From SNMP format to HexaFormat
def changeMacFormat(macaddress):
	result = macaddress.replace(" ",":")
	result = result.replace("\"","")
	result = result.rstrip(":")
	result = result.lstrip(":")
	result = result.lower()	
	return result
	
## 
def main():
	global list_wlc,list_oid_ap,list_oid_client
	servicio = True	
	timePre = 0
	while servicio == True:
		timeNow = datetime.datetime.now()
		minutes = timeNow.minute
		if timePre <> timeNow.minute:
			if minutes == 0 or minutes % 5 == 0:
				syslog.syslog(syslog.LOG_INFO,"------------ INIT mmwirelessV2 -------------- ")
				setDatetimeMeasure()
				clearingAllList()
				timePre = timeNow.minute
				for wlc in list_wlc:
					syslog.syslog(syslog.LOG_INFO,"Start for: %s " % (wlc))
					getInformationBySNMP(list_wlc[wlc])
					getApInformation(list_wlc[wlc])
					getClientInformation(list_wlc[wlc],wlc)
					getRogueApInformation(list_wlc[wlc])
					syslog.syslog(syslog.LOG_INFO,"End for: %s " % (wlc))
				
				savingLogs()
				savingClientSummary()
				savingApSummary()
				savingSummary()
				output = commands.getstatusoutput("bash /home/plataforma/mmimages.sh")
				syslog.syslog(syslog.LOG_INFO,"------------ FINISH mmwirelessV2 -------------- ")
		time.sleep(1)
		#servicio = False
	
if __name__ == "__main__":	
	main()

