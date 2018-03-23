from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
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
from file_read_backwards import FileReadBackwards
import io
import os.path
from django.http import Http404
from django.http import HttpResponse

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

"""
Tuplas (exp, es_regex)
"""
def filtra_linea(filtros, linea):
    print(linea)
    for filtro in filtros:
        if filtro[1]:
            if re.match(filtro[0], linea):
                return True
        elif filtro[0] in linea:
            return True
    return False

def valida_formato(f):
    lf = list(set(f))
    l = "hlutrsbRU"
    for x in lf:
        if not x in l:
            return False
    return True

def linea_formato(linea, formato):
    regex = r'(?P<h>[0-9]{1,3}(\.[0-9]{1,3}){3}) (?P<l>[^\s]+) (?P<u>[^\s]+) (?P<t>\[.+\]) (?P<r>".+") (?P<s>[0-9]{3}) (?P<b>[0-9]+) (?P<R>".+") (?P<U>".+")'
    l = []
    m = re.match(regex, linea)
    if not m is None:
        for x in formato:
            l.append(m.group(x))
    return ' '.join(l)        

def ejecuta_aux(bandera, lst, max_lineas=-1, filtros=None, formato=None):
    p = sp.Popen("%s %s" % (settings.SCRIPT_SECCIONES, bandera), shell=True, stdout=sp.PIPE)
    i = 0
    for l in io.TextIOWrapper(p.stdout, encoding="utf-8"):
        if not formato is None:
            l = linea_formato(l, formato) + "\n"
        if max_lineas > -1 and i >= max_lineas:
            break
        if (filtros is None or len(filtros) == 0) or filtra_linea(filtros, l):
            lst.append(l)
            i += 1

def ejecuta(bandera, max_lineas=-1, filtros=None):
    lst = []
    ejecuta_aux(bandera, lst, max_lineas, filtros)
    return lst

def lee_archivo_aux(archivo, lst, max_lineas=100, filtros=None, formato=None):
    i = 0
    try:
        frb = FileReadBackwards(archivo.strip(), encoding="utf-8")
        for l in frb:
            if not formato is None:
                l = linea_formato(l, formato)
            if i >= max_lineas:
                break
            if (filtros is None or len(filtros) == 0) or filtra_linea(filtros, l):
                lst.append(l + "\n")
                i += 1
    except:
        pass
    finally:
        frb.close()

def lee_archivo(archivo, max_lineas=100, filtros=None):
    lst = []
    lee_archivo_aux(archivo, lst, max_lineas, filtros)
    return lst[::-1]

def lee_rotaciones(archivo, max_lineas=100, filtros=None, formato=None):
    lst = []
    archivo = archivo.strip()
    lee_archivo_aux(archivo, lst, max_lineas, filtros)
    if len(lst) < max_lineas and os.path.exists(archivo + '.1'):
        lee_archivo_aux(archivo + '.1', lst, max_lineas - len(lst), filtros, formato)
    if len(lst) < max_lineas and os.path.exists(archivo + '.1.gz'):
        a = ('%s.1.gz' % archivo).replace('"', '\"').replace("'","\'")
        ejecuta_aux("--gzip '%s'" % a, lst, max_lineas - len(lst), filtros, formato)
    n = 2
    a = ('%s.%d.gz' % (archivo, n)).replace('"', '\"').replace("'","\'")
    while len(lst) < max_lineas and os.path.exists(a):
        ejecuta_aux("--gzip '%s'" % a, lst, max_lineas - len(lst), filtros, formato)
        a = ('%s.%d.gz' % (archivo, n)).replace('"', '\"').replace("'","\'")
        n += 1
    return lst[::-1]

def int_or_0(n):
    try:
        res = int(n)
        return 0 if res < 0 else res
    except:
        return 0

def obten_filtros(request):
    filtros = []
    qr = request.GET.get('qr')
    q = request.GET.get('q')
    if qr:
        filtros.append((qr, True))
    if q:
        filtros.append((q, False))
    return filtros

@login_required(login_url=reverse_lazy('login'))
def monitoreo_usuarios(request):
    context = {
        'usuarios_activos' : ejecuta('--usuarios-activos'),
        'usuarios_grupos' : ejecuta('--usuario-grupos'),
        'usuarios_bloqueados' : ejecuta('--usuarios-bloqueados')
    }
    return render(request, 'secciones/monitoreo_usuarios.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_procesos(request):
    filtros = obten_filtros(request)
    context = {'salida' : ejecuta('--procesos', filtros=filtros)}
    return render(request, 'secciones/monitoreo_procesos.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_red(request):
    context = {
        'interfaces' : ejecuta('--interfaces'),
        'puertos' : ejecuta('--puertos'),
        'conexiones_establecidas' : ejecuta('--conexiones-establecidas'),
        'conexiones_udp' : ejecuta('--conexiones-udp'),
        'estadisticas' : ejecuta('--estadisticas'),
        'iptables' : ejecuta('--iptables')
    }
    return render(request, 'secciones/monitoreo_red.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_autenticacion(request):
    filtros = obten_filtros(request)
    m = request.GET.get('max')
    max_lineas = int_or_0(m) if m else 100
    config = configparser.ConfigParser()
    try:
        config.read(settings.ARCHIVO_CONFIGURACION)
        seccion = config['AUTENTICACION']
        archivo = seccion.get('archivo', '/var/log/auth.log')
    except:
        archivo = '/var/log/auth.log'
    context = {'auth' : lee_rotaciones(archivo, max_lineas=max_lineas, filtros=filtros)}
    return render(request, 'secciones/monitoreo_autenticacion.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_almacenamiento(request):    
    context = {
        'particiones' : ejecuta('--particiones'),
        'memoria' : ejecuta('--memoria'),
        'cpu' : ejecuta('--cpu')
    }
    return render(request, 'secciones/monitoreo_almacenamiento.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_archivos(request):
    filtros = obten_filtros(request)
    m = request.GET.get('max')
    max_lineas = int_or_0(m) if m else 100
    context = {'salida' : ejecuta('-f', max_lineas=max_lineas, filtros=filtros)}
    return render(request, 'secciones/monitoreo_archivos.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_web(request):
    context = {
        'vhosts' : ejecuta('--vhosts'),
        'mods' : ejecuta('--mods'),
        'accesslogs' : ejecuta('--apache-accesslog'),
        'errorlogs' : ejecuta('--apache-errorlog'),
        'hubo_error' : False
    }
    config = configparser.ConfigParser()
    try:
        config.read(settings.ARCHIVO_CONFIGURACION)
        seccion = config['web']
        context['mysql'] = seccion.get('mysql', '/var/log/mysql/error.log')
        context['postgres'] = seccion.get('postgres', '/var/log/postgresql/postgresql-9.6-main.log')
        context['mod_sec'] = seccion.get('mod_sec', '/var/log/apache2/modsec_audit.log')
        context['syslog'] = seccion.get('syslog', '/var/log/syslog')
        context['messages'] = seccion.get('messages', '/var/log/messages')
    except:
        context['hubo_error'] = True
    return render(request, 'secciones/monitoreo_web.html', context)
    
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
            context['archivos'] = [(x, seccion[x]) for x in seccion.keys()]
        except:
            context['hubo_error'] = True
        return context

@login_required(login_url=reverse_lazy('login'))
def bitacora_generica(request, seccion, bitacora):
    filtros = obten_filtros(request)
    m = request.GET.get('max')
    max_lineas = int_or_0(m) if m else 100
    config = configparser.ConfigParser()
    context = {
        'hubo_error' : False,
        'seccion' : seccion,
        'bitacora' : bitacora
    }
    try:
        config.read(settings.ARCHIVO_CONFIGURACION)
        s = config[seccion]
        b = s.get(bitacora, None)
        if b is None:
            context['hubo_error'] = True
        else:
            context['ubicacion'] = b
            context['nombre'] = os.path.basename(b)
            context['archivo'] = lee_rotaciones(b, max_lineas=max_lineas, filtros=filtros)
    except:
        raise Http404()
    return render(request, 'secciones/bitacora_generica.html', context)

@login_required(login_url=reverse_lazy('login'))
def apache_accesslog(request, posicion):
    logs = ejecuta('--apache-access')
    i = int_or_0(posicion)
    if i <= 0 or i > len(logs):
        raise Http404()
    filtros = obten_filtros(request)
    m = request.GET.get('max')
    max_lineas = int_or_0(m) if m else 100
    formato = request.GET.get('f')
    if formato:
        formato = formato.replace(' ', '')
    archivo = None
    if formato and valida_formato(formato):
        archivo = lee_rotaciones(logs[i - 1], max_lineas=max_lineas, filtros=filtros, formato=formato)
    else:
        archivo = lee_rotaciones(logs[i - 1], max_lineas=max_lineas, filtros=filtros)
    context = {
        'archivo' : archivo,
        'ubicacion' : logs[i - 1]
    }
    return render(request, 'secciones/bitacora_acceso.html', context)

@login_required(login_url=reverse_lazy('login'))
def apache_errorlog(request, posicion):
    logs = ejecuta('--apache-error')
    i = int_or_0(posicion)
    if i <= 0 or i > len(logs):
        raise Http404()
    filtros = obten_filtros(request)
    m = request.GET.get('max')
    max_lineas = int_or_0(m) if m else 100
    context = {
        'nombre' : 'de error de Apache',
        'ubicacion' : logs[i - 1],
        'archivo' : lee_rotaciones(logs[i - 1], max_lineas=max_lineas, filtros=filtros),
        'hubo_error' : False
    }
    return render(request, 'secciones/bitacora_generica.html', context)

@login_required(login_url=reverse_lazy('login'))
def graficas(request):
    f = open(os.path.join(settings.BASE_DIR, "secciones/templates/secciones/graficas.html"))
    l = f.read()
    f.close()
    return HttpResponse(l)
