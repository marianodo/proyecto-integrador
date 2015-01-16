from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.http import HttpResponse
from forms import SignUpForm
from control.models import *
#from control.formularios import *
from datetime import datetime,date
from django.contrib.auth.decorators import login_required
import RPi.GPIO as GPIO ## Import GPIO library
import time
import os
import glob
#from datetime import datetime, date
import xlwt
import tablib
import commands

from django.core.servers.basehttp import FileWrapper
import urlparse
from urllib2 import urlopen
from urllib import urlretrieve
from django.conf import settings
import sys
import zipfile
import tempfile
import StringIO

import mimetypes


GPIO.setmode(GPIO.BOARD) ## Use board pin numbering
GPIO.setup(3, GPIO.OUT) #


@login_required()
def home(request): #Vuelve al home, pasamos Flag false ya que no existe llamada en curso
    return render_to_response('home.html', {'user': request.user,"flag":False}, context_instance=RequestContext(request))
    
@login_required()
def mostrarTablaUsuarios(request):
    usuarios = datos_usuarios_dj.objects.all() #Trae todos los usuarios
    return render_to_response('tablaUsuarios.html',{'usuarios': usuarios })

@login_required()
def openDoor(request):
    separarEnter = []
    archivoBuscar = 'asterisk -r -x "sip show channels" ' # Antes de abrir puerta chequea comunciacion
    busqueda = commands.getoutput(archivoBuscar)
    if busqueda.find("Tx") != -1: #Si existe comunicacion establecida, vuelve al home diciendo que tienen que cortar priemro
        return render_to_response('home.html', {'user': request.user,"flag":True}, context_instance=RequestContext(request))           
    foto = os.system("curl http://localhost:8080/0/action/snapshot")
    GPIO.output(3,True) #Abro puerta
    time.sleep(3)
    GPIO.output(3,False)
    username = request.user.username
    id_user= User.objects.get(username=username).pk
    new = Web_eventos_dj(id_usuario_eventos_web=id_user,nombres_eventos_web=username,via_eventos_web="WEB",fechayhora_eventos_web=datetime.now(),lugar_eventos_web="LAC")
    new.save() #Registro quien abrio puerta
    return HttpResponseRedirect("/home")
    

@login_required()
def upService(request): #Si el janus esta caido, se levanta
    os.system("service janus stop")
    time.sleep(1)
    os.system("service janus start")
    return HttpResponseRedirect("/home")

@login_required()
def mostrarTablaEventos(request): # Muestra eventos
    if request.method=="POST": #Si hay post es prque se quiere ver todos los eventos
        eventos = Eventos_dj.objects.order_by('-id')
        return render_to_response('tablaEventos.html',{'usuarios': eventos },RequestContext(request))
    eventos = Eventos_dj.objects.order_by('-id')[:30]
    return render_to_response('tablaEventos.html',{'usuarios': eventos },RequestContext(request))

@login_required()
def mostrarEventosUsuario(request,id_usuario):
    eventos = Eventos_dj.objects.filter(id_usuario_eventos=id_usuario).order_by('-id')
    return render_to_response('eventosUsuario.html',{'usuarios': eventos, 'id_usuario':id_usuario })


@login_required()
def eliminar_usuario(request, id_usuario):
    if request.user.is_superuser: #Para agregar,editar o borrar se necesita ser superuser
        usuario=datos_usuarios_dj.objects.get(id=id_usuario)
        usuario.delete()
        return HttpResponseRedirect("/tablaUsuarios")
    else:
        return HttpResponseRedirect("/error403")

@login_required()
def editarUsuario(request, idUsuario):
    if request.user.is_superuser: 
        if request.method=="POST":
            datos = request.POST
            nombre = datos['nombre']
            apellido = datos['apellido']
            dni = datos['dni']
            telefono = datos['telefono']
            direccion = datos['direccion']
            localidad = datos['localidad']
            email = datos['email']
            clave = datos['clave']
            estado = datos['estado']
            tarjeta = datos['tarjeta']
            categoria = datos['categoria'] #Traigo los datos del post y edito usuario
            usuarioUpdate = datos_usuarios_dj.objects.filter(id=idUsuario).update(nombres_usuario= nombre,apellidos_usuario = apellido,dni_usuario=dni,telefono_usuario=telefono,direccion_usuario=direccion,localidad_usuario=localidad,email_usuario=email,clave_usuario=clave,estado_usuario=estado,tarjeta_usuario=tarjeta,categoria_usuario_id=categoria)
            return HttpResponseRedirect("/tablaUsuarios")
        usuario=datos_usuarios_dj.objects.get(id=idUsuario)
        identPersonals = Personal_dj.objects.all()
        return render_to_response("editarUsuario.html",{"formularios":usuario,'identPersonals':identPersonals},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/error403")
@login_required()
def editarFranja(request, idFranja):
    if request.user.is_superuser:
        if request.method=="POST":
            desdeFranjas = request.POST['desdeFranjas']
            hastaFranjas= request.POST['hastaFranjas']
            franjasUpdate = Franjas_horarias_dj.objects.filter(id=idFranja).update(desde_franjas= desdeFranjas,hasta_franjas = hastaFranjas)
            return HttpResponseRedirect("/tablaFranjas")
        franja = Franjas_horarias_dj.objects.get(id=idFranja)
        return render_to_response("editarFranja.html",{"formularios":franja},context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/error403")

def capturar(request):
    identPersonals = Personal_dj.objects.all()
    code = "" #Esta funcion es para capturar la clave de una tarjeta
    flag = 0
    while (code == "" and flag < 10):
        try:
            codes = Captura_clave.objects.get(id=1)
            code = codes.clave_captura #Si la clave es capturada se guarda en la BD y de aca lee
            
        except:
            flag += 1 #Si no se captura salta error y vuelve a intentar hasta 10 intentos
            time.sleep(1)

    if code == "": #Si no se encontro la clave, se advierte
        code = "No_se_encontro"
    return render(request, 'agregarUsuario.html', {'identPersonals':identPersonals, 'clave': code})



@csrf_protect
def showphoto(request):
    if request.method == 'POST': #Se muestra foto del dia actual y del dia especificado
        dateFrom = request.POST['from']
        pathTotal = "/usr/src/web/login/static/photo/" + dateFrom + "*.jpg"
        photoFiles = glob.glob(pathTotal)
        if dateFrom == '':
            dateFrom = "Todas las fotos"
    else:
        dateFrom = time.strftime("%d-%m-%Y")
        pathTotal = "/usr/src/web/login/static/photo/" + dateFrom + "*.jpg"
        photoFiles = glob.glob(pathTotal)
    photo = []
    for photoFile in photoFiles:
        photoPath = photoFile.split("/")
        photo.append(photoPath[7]) #Agrego las fotos en una lista
    photo.sort() # Ordeno la lista
    photo.reverse()
    dateFrom = dateFrom + " (Se encontraron " + str(len(photo)) + " fotos)"
    return render_to_response('showphoto.html',{'photos': photo, 'dateFrom': dateFrom },RequestContext(request))

@csrf_protect
def usershowphoto(request,dateFrom):
    pathTotal = "/usr/src/web/login/static/photo/" + dateFrom + "*.jpg"
    photoFiles = glob.glob(pathTotal)     
    photo = []
    for photoFile in photoFiles:
        photoPath = photoFile.split("/")
        photo.append(photoPath[7]) #Agrego las fotos en una lista
    photo.sort() # Ordeno la lista
    photo.reverse()
    dateFrom = dateFrom + " (Se encontraron " + str(len(photo)) + " fotos)"
    return render_to_response('showphoto.html',{'photos': photo, 'dateFrom': dateFrom },RequestContext(request))      
    
@login_required()
def WebEventos(request):
    if request.method=="POST": #Muestra todos los eventos via web
        eventosweb = Web_eventos_dj.objects.order_by('-id')
        return render_to_response('tablaWebEventos.html',{'usuariosWeb': eventosweb },RequestContext(request))
    eventosweb = Web_eventos_dj.objects.order_by('-id')[:50]
    return render_to_response('tablaWebEventos.html',{'usuariosWeb': eventosweb },RequestContext(request))

@login_required()
def mostrarEventosUsuarioWeb(request,id_usuario):
    if request.method=="POST": #Muestra los eventos web por usuario
        eventosweb = Web_eventos_dj.objects.filter(id_usuario_eventos_web=id_usuario).order_by('-id')
        return render_to_response('eventosUsuarioWeb.html',{'usuariosWeb': eventosweb })
    eventosweb = Web_eventos_dj.objects.filter(id_usuario_eventos_web=id_usuario).order_by('-id')[:5]
    return render_to_response('eventosUsuarioWeb.html',{'usuariosWeb': eventosweb })

@csrf_protect
def addUser(request):
    if request.user.is_superuser: #Agregar un usuario nuevo
        identPersonals = Personal_dj.objects.all()
        if request.method == 'POST':
            datos = request.POST
            nombre = datos['nombre']
            apellido = datos['apellido']
            dni = datos['dni']
            telefono = datos['telefono']
            direccion = datos['direccion']
            localidad = datos['localidad']
            email = datos['email']
            clave = datos['clave']
            estado = datos['estado']
            tarjeta = datos['tarjeta']
            fechaalta = datetime.now()
            categoria = datos['categoria']
            busquedaClave = datos_usuarios_dj.objects.filter(clave_usuario=clave).first()
            if (busquedaClave == None):
                datosusr = datos_usuarios_dj(nombres_usuario=nombre,apellidos_usuario=apellido,dni_usuario=dni,telefono_usuario=telefono,direccion_usuario=direccion,localidad_usuario=localidad,email_usuario=email,clave_usuario=clave,estado_usuario=estado,tarjeta_usuario=tarjeta,fecha_alta_usuario=fechaalta,categoria_usuario_id=categoria) 
                datosusr.save()
                usuarios = datos_usuarios_dj.objects.all()
                return render_to_response('tablaUsuarios.html',{'usuarios': usuarios},RequestContext(request))
            else:
                return render_to_response('agregarUsuario.html',{'identPersonals':"True",'user': request.user},RequestContext(request))
        return render_to_response('agregarUsuario.html',{'identPersonals':identPersonals,'user': request.user},RequestContext(request))
    else:
        return HttpResponseRedirect("/error403")

@login_required()
def mostrartablaNoPermitidoEventos(request): #Muestra tabla de aquellas tarjetas leidas que no tienen acceso
    if request.method == 'POST':
        eventos = Eventos_no_Permitidos_dj.objects.all().order_by('-id')
        return render_to_response('tablaNoPermitidoEventos.html',{'eventos': eventos },RequestContext(request))
    eventos = Eventos_no_Permitidos_dj.objects.all().order_by('-id')[:50]
    return render_to_response('tablaNoPermitidoEventos.html',{'eventos': eventos },RequestContext(request))

def macadr(request):
    return render_to_response('macadr.html',RequestContext(request))

@csrf_exempt    
def exportarAExcel (request,name): #Exporta la tabla deseada en "name" a archivo en excel
    if name <> "usuarios":
        
        datos = request.POST
        count = datos['cantidad']
        if name == 'eventos':
            if count == 2000:
                values_list = Eventos_dj.objects.order_by('-id').values_list()
            else:
                values_list = Eventos_dj.objects.order_by('-id')[:int(count)].values_list()
        if name == 'eventosweb':
            if count == 2000:
                values_list = Web_eventos_dj.objects.order_by('-id').values_list()
            else:
                values_list = Web_eventos_dj.objects.order_by('-id')[:int(count)].values_list()
        if name == 'eventosNoPermitidos':
            if count == 2000:
                values_list = Eventos_no_Permitidos_dj.objects.order_by('-id').values_list()
            else:
                values_list = Eventos_no_Permitidos_dj.objects.order_by('-id')[:int(count)].values_list()
        if name == 'eventosFecha':
            values_list = Eventos_dj.objects.filter(fechayhora_eventos__contains = count).values_list()
        if name == 'eventosFechaWeb':
            values_list = Web_eventos_dj.objects.filter(fechayhora_eventos_web__contains = count).values_list()
            
    else:
        values_list = datos_usuarios_dj.objects.all().values_list()

    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('untitled')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy hh:mm')
    date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')

    for row, rowdata in enumerate(values_list):
        for col, val in enumerate(rowdata):
            if isinstance(val, datetime):
                style = datetime_style
            elif isinstance(val, date):
                style = date_style
            else:
                style = default_style

            sheet.write(row, col, val, style=style)

    
    response = HttpResponse(content_type="application/vnd.ms-excel")
    stringName = name + ".xls"
    response['Content-Disposition'] = 'attachment; filename=' + stringName
    book.save(response)
    usuarios = datos_usuarios_dj.objects.all()
    return response

@csrf_exempt    
def exportarEventoUser(request,idUser): #Exporta la tabla deseada en "name" a archivo en excel
    
    values_list = Eventos_dj.objects.filter(id_usuario_eventos=idUser).order_by('-id').values_list()

    book = xlwt.Workbook(encoding='utf-8')
    sheet = book.add_sheet('untitled')
    default_style = xlwt.Style.default_style
    datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy hh:mm')
    date_style = xlwt.easyxf(num_format_str='dd/mm/yyyy')

    for row, rowdata in enumerate(values_list):
        for col, val in enumerate(rowdata):
            if isinstance(val, datetime):
                style = datetime_style
            elif isinstance(val, date):
                style = date_style
            else:
                style = default_style

            sheet.write(row, col, val, style=style)

    
    response = HttpResponse(content_type="application/vnd.ms-excel")
    stringName =  "eventosUsuario.xls"
    response['Content-Disposition'] = 'attachment; filename=' + stringName
    book.save(response)
    usuarios = datos_usuarios_dj.objects.all()
    return response

@login_required()
def mostrarFranjasHorarias(request):
    identPersonals = Personal_dj.objects.all()
    if request.method=="POST": #Muestra una franja horaria en especial
        idPersonal = request.POST['idPersonal']
        namePersonal = Personal_dj.objects.get(pk=idPersonal)
        Franjas = namePersonal.franjas_horarias_dj_set.all().order_by('dia_franjas')
        return render_to_response('tablaFranjas.html',{'Franjas': Franjas ,'identPersonals':identPersonals,'namePersonal':namePersonal}, context_instance=RequestContext(request))
    try:
        namePersonal = Personal_dj.objects.first() #Muestra la primer franja horaria que aparece en la BD
        Franjas = namePersonal.franjas_horarias_dj_set.all().order_by('dia_franjas')
        return render_to_response('tablaFranjas.html',{'Franjas': Franjas ,'identPersonals':identPersonals,'namePersonal':namePersonal}, context_instance=RequestContext(request))
    except: #Si no existe ninguna categoria, se redirecciona automaticamente para agregar una uneva
        return render_to_response('agregarPersonal.html', context_instance=RequestContext(request))

@login_required()
def borrarFranja(request, idFranja):
    if request.user.is_superuser:
        identPersonals = Personal_dj.objects.all()
        deleteFranja = Franjas_horarias_dj.objects.get(id=idFranja)
        idNamePersonal = deleteFranja.id_personal_franjas
        deleteFranja.delete()
        namePersonal = Personal_dj.objects.get(pk=idNamePersonal.id)
        Franjas = namePersonal.franjas_horarias_dj_set.all().order_by('dia_franjas')
        return render_to_response('tablaFranjas.html',{'Franjas': Franjas ,'identPersonals':identPersonals,'namePersonal':namePersonal}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/error403")

@login_required()
@csrf_protect
def agregarFranja(request):
    if request.user.is_superuser:   
        if request.method=="POST":
            diaFranja = request.POST['diaFranja']
            idPersonal = request.POST['idPersonal']
            desdeFranja = request.POST['desdeFranja'] 
            hastaFranja = request.POST['hastaFranja'] 
            datoFranja = Franjas_horarias_dj(id_personal_franjas_id = idPersonal ,dia_franjas_id = diaFranja,desde_franjas = desdeFranja, hasta_franjas = hastaFranja) 
            datoFranja.save()
        identPersonals = Personal_dj.objects.all()
        namePersonal = Personal_dj.objects.get(pk=idPersonal)
        Franjas = namePersonal.franjas_horarias_dj_set.all().order_by('dia_franjas')
        return render_to_response('tablaFranjas.html',{'Franjas': Franjas ,'identPersonals':identPersonals,'namePersonal':namePersonal}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/error403")
@login_required()
@csrf_protect
def agregarPersonal(request):
    if request.user.is_superuser:
        if request.method=="POST":
            identificacion = request.POST['identificacion']
            IdentificacionPers = Personal_dj(identificacion_personal = identificacion) 
            IdentificacionPers.save()
        personal = Personal_dj.objects.all()
        return render_to_response('agregarPersonal.html',{'personal': personal },context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/error403")
@login_required()
def borrarPersonal(request, idPersonal):
    if request.user.is_superuser:
        personal = Personal_dj.objects.all()
        deletePersonal = Personal_dj.objects.get(id=idPersonal)
        deletePersonal.delete()
        
        return render_to_response('agregarPersonal.html',{'personal':personal}, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/error403")
@login_required()
def ayuda(request):
    return render_to_response('ayuda.html', {'user': request.user}, context_instance=RequestContext(request))

@login_required()
def error403(request):
    return render_to_response('403.html', context_instance=RequestContext(request))

@login_required()    
def file_download(request,filename):

    filepath = os.path.join(settings.MEDIA_ROOT, filename)
    wrapper = FileWrapper(open(filepath, "rb"))
    content_type = mimetypes.guess_type(filepath)[0]
    response = HttpResponse(wrapper, content_type="application/octet-stream")
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
    
@login_required()
def reset(request):
    if request.user.is_superuser:
        a = os.system ("reboot")
        return HttpResponseRedirect("/home")
    else:
        return HttpResponseRedirect("/error403")