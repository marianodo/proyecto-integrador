#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import serial
import RPi.GPIO as GPIO ## Import GPIO library
import time
import os
import commands
import threading
global lugar
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(3, GPIO.OUT) ## Setup GPIO Pin 7 to OUT
lugar = 'LAC'
threads = list()
#dias = {'Monday': 1 ,'Tuesday': 2 ,'Wednesday': 3 ,'Thursday': 4 ,'Friday': 5 , 'Saturday': 6 , 'Sunday' : 7}
def connect():
        serialPort = serial.Serial("/dev/ttyAMA0", 1200, timeout=0.5, rtscts=False, dsrdtr=False, xonxoff=False,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE)
        return serialPort

def readRfid(serialPort):
        while 1:
                userCode = serialPort.readline()
                
                if (len(userCode) > 6):
                        vectorRfid = []
                        vectorRfid =  userCode.split(chr(13).encode('ascii'))
                        rfid = vectorRfid[0]
                        thpicture = threading.Thread(target=takePicture)
                        threads.append(thpicture)
                        thpicture.start()
                        return rfid

def conectBD():
        db = sqlite3.connect('/usr/src/web/database.sqlite')
        cursor = db.cursor()
        
        dataBase = []
        dataBase.append(db)
        dataBase.append(cursor)                                                 
        return dataBase

def captureCode(rfid):
        
        try:
                db = sqlite3.connect('/usr/src/web/database.sqlite')
                cursor = db.cursor()
                mi_query = "INSERT INTO control_captura_clave (id,clave_captura,lugar_captura) VALUES ('1','%s','LAC')"%(rfid)
                cursor.execute(mi_query)
                db.commit()
                time.sleep(5)

                mi_query= "DELETE FROM control_captura_clave WHERE id='1'"
                cursor.execute(mi_query)
                db.commit()
        except:
		mi_query = "DELETE FROM control_captura_clave WHERE id ='1'"
		cursor.execute(mi_query)
		db.commit()


def openDoor():
        GPIO.output(3,True)
        time.sleep(2)
        GPIO.output(3,False)

def registerEvent(db,cursor,user):
        idUser = user[0]
        firstName = user[1]
        lastName = user[2]
        mi_query = "INSERT INTO control_eventos_dj(id_usuario_eventos, nombres_eventos, apellidos_eventos, fechayhora_eventos, lugar_eventos) VALUES ('%s','%s','%s',DATETIME('now','localtime'),'LAC')"%(idUser,firstName,lastName)
        cursor.execute(mi_query)
        db.commit()
        
def checkTime(db,cursor,idUser):
        today = time.strftime("%w")
        mi_query = "SELECT desde_franjas,hasta_franjas FROM control_datos_usuarios_dj usr join control_franjas_horarias_dj franjas on usr.categoria_usuario_id = franjas.id_personal_franjas_id where usr.id = '%i' and franjas.dia_franjas_id = '%s'"%(idUser,today)
        cursor.execute(mi_query)
        users = cursor.fetchall()
        now = time.strftime("%X")
        for user in users:
                desde = user[0].replace(":","")
                hasta = user[1].replace(":","")
                ahora = now.replace(":","")
                
                if int(ahora) >= int(desde) and int(ahora) <= int(hasta):
                        openDoor()
                else:
                        pass
def searchUser(rfid,db,cursor):
        
        mi_query = "SELECT * FROM control_datos_usuarios_dj WHERE clave_usuario = '%s'"%(rfid)
        cursor.execute(mi_query)
        user = cursor.fetchone()
        #ACA VA SACAR FOTO
        if user <> None:
                estado = user[9]
                idUser = user[0]
                if estado == 'ACTIVO':
                        checkTime(db,cursor,idUser)
                registerEvent(db,cursor,user)
        else:
                registerFailedEvent(db,cursor,rfid)
                

def registerFailedEvent(db,cursor,rfid):
        if rfid[5:]<>"00000":
                mi_query = "INSERT INTO control_eventos_no_permitidos_dj(clave_eventos_no_permitido, fechayhora_eventos_no_permitido, lugar_eventos_no_permitido) VALUES ('%s',DATETIME('now','localtime'),'LAC')"%(rfid)
                cursor.execute(mi_query)
                db.commit()


def takePicture():
        separarEnter = []
        archivoBuscar = 'asterisk -r -x "sip show channels" ' # Antes de abrir puerta chequea comunciacion
        busqueda = commands.getoutput(archivoBuscar)
        if busqueda.find("Tx") != -1: #Si existe comunicacion establecida, vuelve al home diciendo que tienen que cortar priemro
                pass
        else:
                foto = os.system("curl http://localhost:8080/0/action/snapshot")

if __name__ == '__main__':

        serialPort = connect()
        while 1:
                rfid = readRfid(serialPort)
                cursordb = conectBD()
                db = cursordb[0]
                cursor = cursordb[1]
                searchUser(rfid,db,cursor)
		t = threading.Thread(target=captureCode, args=(rfid,))
                threads.append(t)
                t.start()

                

