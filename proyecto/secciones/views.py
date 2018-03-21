from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeletionMixin, UpdateView
from django.views.generic import CreateView, ListView, DetailView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .models import Seccion
from .forms import SeccionForm
from django.urls import reverse_lazy
from django.conf import settings
import configparser
import subprocess as sp
import re

class NuevaSeccion(LoginRequiredMixin, CreateView):

    model = Seccion
    form_class = SeccionForm
    template_name = 'secciones/nueva_seccion.html'
    success_url = reverse_lazy('administrar-secciones')

class ListarSecciones(LoginRequiredMixin, ListView):

    model = Seccion
    context_object_name = 'secciones'
    template_name = 'secciones/administrar_secciones.html'

class VistaSeccion(LoginRequiredMixin, DetailView):

    model = Seccion
    template_name = 'secciones/seccion.html'
    context_object_name = 'seccion'

class EditarSeccion(LoginRequiredMixin, UpdateView):

    model = Seccion
    form_class = SeccionForm
    template_name = 'secciones/editar_seccion.html'
    success_url = reverse_lazy('administrar-secciones')
        
class EliminarSeccion(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    
    model = Seccion
    success_url = reverse_lazy('administrar-secciones')
    success_message = 'Sección eliminada'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarSeccion, self).delete(request, *args, **kwargs)

def ejecuta(bandera):
    p = sp.Popen("%s %s" % (settings.SCRIPT_SECCIONES, bandera), shell=True, stdout=sp.PIPE)
    output = p.stdout.read()
    return output.decode('utf-8')

def monitoreo_usuarios(request):
    context = {
        'usuarios_activos' : ejecuta('--usuarios-activos'),
        'usuarios_grupos' : ejecuta('--usuario-grupos'),
    }
    return render(request, 'secciones/monitoreo_usuarios.html', context)

def monitoreo_procesos(request):
    context = {'salida' : ejecuta('--procesos')}
    return render(request, 'secciones/monitoreo_procesos.html', context)

def monitoreo_red(request):
    context = {
        'interfaces' : ejecuta('--interfaces'),
        'puertos' : ejecuta('--puertos'),
        'conexiones_establecidas' : ejecuta('--conexiones-establecidas'),
        'estadisticas' : ejecuta('--estadisticas')
        # 'iptables' : ejecuta('--iptables')
    }
    return render(request, 'secciones/monitoreo_red.html', context)

def monitoreo_autenticacion(request):
    context = {'salida' : ejecuta('-u')}
    return render(request, 'secciones/monitoreo_autenticacion.html', context)

def monitoreo_almacenamiento(request):
    context = {'salida' : ejecuta('-u')}
    return render(request, 'secciones/monitoreo_almacenamiento.html', context)

def monitoreo_archivos(request):
    context = {'salida' : ejecuta('-f')}
    return render(request, 'secciones/monitoreo_archivos.html', context)

def monitoreo_web(request):
    context = {'salida' : ejecuta('-u')}
    return render(request, 'secciones/monitoreo_web.html', context)

def lee_bitacora(archivo):
    p = sp.Popen("%s --archivo '%s'" % (settings.SCRIPT_SECCIONES, archivo.replace("'", "\\'")), shell=True, stdout=sp.PIPE)
    output = p.stdout.read()
    return output.decode('utf-8')
    
class MonitoreoGenerico(LoginRequiredMixin, DetailView):

    model = Seccion
    template_name = 'secciones/monitoreo_generico.html'
    context_object_name = 'seccion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hubo_error'] = False
        config = configparser.ConfigParser()
        seccion = None
        try:
            config.read(settings.ARCHIVO_CONFIGURACION)
            seccion = config[self.kwargs['slug']]
        except:
            context['hubo_error'] = True
        context['archivos'] = [] if seccion is None else [(x, lee_bitacora(x)) for x in seccion.values()]
        return context
