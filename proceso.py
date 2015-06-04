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
def writeFileLed(status, source):
	try:
		File = open("/var/tmp/statusLed.txt","r+")
	except:
		File = open("/var/tmp/statusLed.txt","w+")
	if source == "ping":
		File.readline()
	File.write(status + "\n")
	File.close()
def checkPy(archivo):
	separarEnter = []
	archivoBuscar = "ps aux | grep " + archivo + ".py"
	
	busqueda = commands.getoutput(archivoBuscar)
	separarEnter = busqueda.split('\n')
	
	
	if len(separarEnter) < 3:
		if archivo =="manage":
			archivo = "djangoservice"

		data = time.strftime("%c") + ' - ' +" El proceso " + archivo + " esta caido."
		writeFile(data)
		if archivo == "control":
			writeFileLed("1","control")
		levantarArchivo = "service " + archivo + " start"
		a = os.system(levantarArchivo)
		sendEmail(archivo)
		time.sleep(3)
	else:
		if archivo == "control":
			writeFileLed("0","control")

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
        print "Chequeando si el proceso " + archivo + " esta funcionando"
	if len(separarEnter) < 3:
		data = time.strftime("%c") + ' - ' +" El proceso " + archivo + " esta caido"
		writeFile(data)
		a = os.system(levantarArchivo)
		sendEmail(archivo)
		time.sleep(3)
def checkPing():
	hostname = "192.168.1.50"
	response = os.system("ping -c 1 " + hostname)

	if response == 0:
	  writeFileLed("0","ping")
	else:
	  writeFileLed("1","ping")

if __name__ == '__main__':
	checkPy("control")
	checkPy("manage")
	checkOther("janus")
	checkOther("motion")
	checkOther("twinkle")
	checkPing()

	
