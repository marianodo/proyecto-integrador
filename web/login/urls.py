from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'login.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^$', 'control.views.main', name='main'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^signup$', 'control.views.signup', name='signup'),
    url(r'^$', login, {'template_name': 'login.html', }, name="login"),
    url(r'^home$', 'control.views.home', name='home'),
    url(r'^logout$', logout, {'template_name': 'login.html', }, name="logout"),
    url(r'^openDoor', 'control.views.openDoor', name='openDoor'),
    url(r'^tablaUsuarios$', 'control.views.mostrarTablaUsuarios', name='tablaUsuarios'),
    url(r'^tablaEventos', 'control.views.mostrarTablaEventos', name='tablaEventos'),
    url(r'^capturar', 'control.views.capturar'),
    url(r'borrar/(?P<id_usuario>\d+)$','control.views.eliminar_usuario'),
    url(r'editarUsuario/(?P<idUsuario>\d+)$','control.views.editarUsuario'),
    url(r'^eventosUsuario/(?P<id_usuario>\d+)$', 'control.views.mostrarEventosUsuario', name='eventosUsuario'),
    url(r'^showphoto', 'control.views.showphoto', name='showphoto'),
    url(r'^tablaWebEventos$', 'control.views.WebEventos', name='WebEventos'),
    url(r'^eventosUsuarioWeb/(?P<id_usuario>\d+)$', 'control.views.mostrarEventosUsuarioWeb', name='eventosUsuarioWeb'),
    url(r'^agregarUsuario', 'control.views.addUser', name='addUser'),
    url(r'^tablaNoPermitidoEventos', 'control.views.mostrartablaNoPermitidoEventos', name='tablaNoPermitidoEventos'),
    url(r'^macadr', 'control.views.macadr'),
    url(r'^export/(?P<name>[-\w]+)$', 'control.views.exportarAExcel', name='exportarAExcel'),
    url(r'^exportar', 'control.views.exportar', name='exportar'),
    #url(r'^exportlimited', 'control.views.exportarAExcelLimitado', name='exportarAExcelLimitado'),
    url(r'^upService', 'control.views.upService', name='upService'),
    url(r'^tablaFranjas', 'control.views.mostrarFranjasHorarias', name='franjasHorarias'),
    url(r'^borrarFranja/(?P<idFranja>\d+)$', 'control.views.borrarFranja', name='borrarFranja'),
    url(r'^agregarFranja', 'control.views.agregarFranja', name='agregarFranja'),
    url(r'^agregarPersonal', 'control.views.agregarPersonal', name='agregarPersonal'),
    url(r'^borrarPersonal/(?P<idPersonal>\d+)$', 'control.views.borrarPersonal', name='borrarPersonal'),
    url(r'editarFranja/(?P<idFranja>\d+)$','control.views.editarFranja'),
    url(r'^ayuda', 'control.views.ayuda', name='ayuda'),
    url(r'^error403', 'control.views.error403', name='error403'),
)
