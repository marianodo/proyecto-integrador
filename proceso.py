import commands
import os
import time
from sendEmail import responseEmail

def sendEmail(archivo):
	mensaje = "Proceso "+ archivo + " dejo de funcionar. Verificar"
	asunto = "Error en proceso " + archivo
	mailfrom = "vigilancialac@gmail.com"
	responseEmail(mailfrom,mensaje, asunto).send() # Respondo el email con msj erroneo
def writeFile(data):
	File = open("/var/log/logFile.txt","a+")
	File.readline()
	File.seek(0)
	File.write(data)
	File.close()
def checkPy(archivo):
	separarEnter = []
	archivoBuscar = "ps aux | grep " + archivo + ".py"
	
	busqueda = commands.getoutput(archivoBuscar)
	separarEnter = busqueda.split('\n')

	if len(separarEnter) < 3:
		if archivo =="manage":
			archivo = "djangoservice"

		data = time.strftime("%c") + ' - ' +" El proceso " + archivo + " esta caido." + "\n"
		writeFile(data)
		levantarArchivo = "service " + archivo + " start"
		a = os.system(levantarArchivo)
		sendEmail(archivo)
		time.sleep(3)


def checkOther(archivo):
	if archivo == 'motion':
		levantarArchivo = "motion -n"
	elif archivo == 'janus':
		levantarArchivo = "service janus start"
	else:
		levantarArchivo = "twinkle -c"

	separarEnter = []
	archivoBuscar = "ps aux | grep " + archivo
	busqueda = commands.getoutput(archivoBuscar)
	separarEnter = busqueda.split('\n')
	if len(separarEnter) < 3:
		data = time.strftime("%c") + ' - ' +" El proceso " + archivo + " esta caido \n"
		writeFile(data)
		a = os.system(levantarArchivo)
		time.sleep(3)


if __name__ == '__main__':
	checkPy("control")
	checkPy("manage")
	checkOther("janus")
	checkOther("motion")
	checkOther("twinkle")
	