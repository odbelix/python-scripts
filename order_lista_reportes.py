#Ordenar lista de Reportes
import os
from os.path import isfile, join

lista_archivos = []
lista_archivos_orden = []

		
#Path="/var/www/application/mobmeters/static/reports/"
Path = "/home/mmoscoso/Documentos/workspace/python-scripts/"

for files in os.listdir(Path):
	if isfile(join(Path,files)):
		lista_archivos.append(files)

text = ""
for x in sorted(lista_archivos):
    arr_name = x.split("_")
    if text <> arr_name[0]:
		print "----->%s/%s/%s" % (arr_name[0][0:4],arr_name[0][4:6],arr_name[0][6:8])
		text = arr_name[0]
		
    print arr_name[0]
    lista_archivos_orden.append(x)
#t = loader.get_template('listreports.html')
#variables
	#lista_archivos_orden = lista_archivos.sort()
#c = Context({
#	'lista_archivos':lista_archivos,
#})
   #return HttpResponse(t.render(c))

print lista_archivos_orden
