from django.db import models

# Create your models here.
class Personal_dj(models.Model):
    id = models.AutoField(primary_key=True)
    identificacion_personal = models.CharField(max_length=30)
    
class datos_usuarios_dj(models.Model):
    id = models.AutoField(primary_key=True)
    nombres_usuario = models.CharField(max_length=30)
    apellidos_usuario = models.CharField(max_length=30)
    dni_usuario = models.IntegerField()
    telefono_usuario = models.CharField(max_length=30)
    direccion_usuario = models.CharField(max_length=30)
    localidad_usuario = models.CharField(max_length=30)
    email_usuario = models.CharField(max_length=30)
    clave_usuario = models.CharField(max_length=30)
    estado_usuario = models.CharField(max_length=30)
    tarjeta_usuario = models.CharField(max_length=30)
    fecha_alta_usuario = models.DateTimeField()
    categoria_usuario = models.ForeignKey(Personal_dj)

class Eventos_dj(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario_eventos= models.IntegerField()
    nombres_eventos = models.CharField(max_length=50)
    apellidos_eventos = models.CharField(max_length=50)
    fechayhora_eventos = models.DateTimeField()
    lugar_eventos= models.CharField(max_length=50)

class Captura_clave(models.Model):
    clave_captura = models.CharField(max_length=50)
    lugar_captura = models.CharField(max_length=50)

class Web_eventos_dj(models.Model):
    id = models.AutoField(primary_key=True)
    id_usuario_eventos_web= models.IntegerField()
    nombres_eventos_web = models.CharField(max_length=50)
    via_eventos_web = models.CharField(max_length=50)
    fechayhora_eventos_web = models.DateTimeField()
    lugar_eventos_web= models.CharField(max_length=50)
    
class Eventos_no_Permitidos_dj(models.Model):
    id = models.AutoField(primary_key=True)
    clave_eventos_no_permitido = models.CharField(max_length=50)
    fechayhora_eventos_no_permitido = models.DateTimeField()
    lugar_eventos_no_permitido= models.CharField(max_length=50)



class Dias_semanales_dj(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_dias = models.CharField(max_length=10)
    
class Franjas_horarias_dj(models.Model):
    id = models.AutoField(primary_key=True)
    id_personal_franjas = models.ForeignKey(Personal_dj)
    dia_franjas = models.ForeignKey(Dias_semanales_dj)
    desde_franjas = models.TimeField()
    hasta_franjas = models.TimeField()

