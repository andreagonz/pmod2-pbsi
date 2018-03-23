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
    """
    Clase para crear una nueva sección personalizada.
    """
    model = Seccion
    form_class = SeccionForm
    template_name = 'secciones/nueva_seccion.html'
    success_url = reverse_lazy('administrar-secciones')

class ListarSecciones(LoginRequiredMixin, ListView):
    """
    Clase para listar las secciones personalizadas.
    """
    model = Seccion
    context_object_name = 'secciones'
    template_name = 'secciones/administrar_secciones.html'

class EditarSeccion(LoginRequiredMixin, UpdateView):
    """
    Clase para editar una sección personalizada.
    """
    model = Seccion
    form_class = SeccionForm
    template_name = 'secciones/editar_seccion.html'
    success_url = reverse_lazy('administrar-secciones')
        
class EliminarSeccion(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Clase para eliminar una sección personalizada.
    """
    model = Seccion
    success_url = reverse_lazy('administrar-secciones')
    success_message = 'Sección eliminada'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarSeccion, self).delete(request, *args, **kwargs)

def filtra_linea(filtros, linea):
    """
    Evalúa si una cadena concuerda con una lista de filtros.
    Recibe:
        filtros (list) - la lista de filtros, cada filtro es una tupla
            t de la forma t = (cadena, bool), donde cadena es la expresión
           con la que se evaluará la línea, y si bool es True se toma a la cadena
           como expresión regular, de lo contrario se toma textualmente.
        linea - cadena a ser evaluada.
    Regresa:
        bool - True si la cadena concuerda con algun filtro de la lista.
    """
    print(linea)
    for filtro in filtros:
        if filtro[1]:
            if re.match(filtro[0], linea):
                return True
        elif filtro[0] in linea:
            return True
    return False

def valida_formato(f):
    """
    Dice si f es un formato válido para la bitácora access de Apache.
    Recibe:
        f (str) - el formato
    Regresa:
        bool - True sólo si f es un formato válido
    """
    lf = list(set(f))
    l = "hlutrsbRU"
    for x in lf:
        if not x in l:
            return False
    return True

def linea_formato(linea, formato):
    """
    Regresa una cadena de la bitácora de acceso de Apache con el formato
    especificado.
    Recibe:
        linea (str) - la cadena a la cual se le aplica el formato.
        formato (str) - el formato especificado.
    Regresa:
        str - la cadena modificada con el formato.
    """
    regex = r'(?P<h>[0-9]{1,3}(\.[0-9]{1,3}){3}) (?P<l>[^\s]+) (?P<u>[^\s]+) (?P<t>\[.+\]) (?P<r>".+") (?P<s>[0-9]{3}) (?P<b>[0-9]+) (?P<R>".+") (?P<U>".+")'
    l = []
    m = re.match(regex, linea)
    if not m is None:
        for x in formato:
            l.append(m.group(x))
    return ' '.join(l)        

def ejecuta_aux(bandera, lst, max_lineas=-1, filtros=None, formato=None):
    """
    Ejecuta el script de la aplicación utilizando una bandera, aplica los filtros con el
    formato indicado (en el caso de la bitácora de acceso de Apache) y regresa un número máximo
    de líneas.
    Recibe:
        bandera (str) - bandera a ser utilizada para el script.
        lst (list) - lista en la que se guardará la salida del script.
        max_lineas (int) - número máximo de líneas a ser regresadas.
        filtros (list) - lista de filtros a ser aplicados a cada línea de la salida
            del script.
        formato (str) - formato que se le aplicará a cada línea (de la bitácora de acceso).
    """
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
    """
    Ejecuta el script de la aplicación con la bandera indicada, filtros y un
    máximo de líneas.
    Recibe:
        bandera (str) - bandera a ser utilizada para el script.
        max_lineas (int) - número máximo de líneas a ser regresadas.
        filtros (list) - lista de filtros a ser aplicados a cada línea de la salida
            del script.
    Regresa:
        list - lista con la salida del script.
    """
    lst = []
    ejecuta_aux(bandera, lst, max_lineas, filtros)
    return lst

def lee_archivo(archivo, lst, max_lineas=100, filtros=None, formato=None):
    """
    Lee de manera inversa un máximo de líneas del archivo indicado aplicando filtros
    y un formato indicado.    
    """
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

def lee_rotaciones(archivo, max_lineas=100, filtros=None, formato=None):
    """
    Lee un archivo y sus rotaciones, regresa un número máximo de las entradas más actuales,
    aplicando filtros y un formato (en el caso de la bitácora de acceso de Apache).
    Recibe:
        archivo (str) - archivo a ser leido.
        max_lineas (int) - número máximo de líneas a ser leídas.
        filtros (list) - lista de filtros a ser aplicados.
        formato (str) - formato a ser aplicado a la bitácora de acceso.
    Regresa:
        list - lista de cadenas con las entradas leídas del archivo y sus rotaciones.
    """
    lst = []
    archivo = archivo.strip()
    # lee_archivo(archivo, lst, max_lineas, filtros)
    archivo = archivo.replace('"', '\"').replace("'","\'")
    ejecuta_aux("--lee-archivo '%s'" % archivo, lst, max_lineas, filtros, formato)
    if len(lst) < max_lineas and len(ejecuta("--existe '%s.1'" % archivo)) > 0:
        ejecuta_aux("--lee-archivo '%s.1'" % archivo, lst, max_lineas - len(lst), filtros, formato)
        # lee_archivo(archivo + '.1', lst, max_lineas - len(lst), filtros, formato)
    if len(lst) < max_lineas and len(ejecuta("--existe '%s.1.gz'" % archivo)) > 0:
        ejecuta_aux("--gzip '%s.1.gz'" % archivo, lst, max_lineas - len(lst), filtros, formato)
    n = 2
    while len(lst) < max_lineas and len(ejecuta("--existe '%s.%d.gz'" % (archivo, n))) > 0:
        ejecuta_aux("--gzip '%s.%d'" % (archivo, n), lst, max_lineas - len(lst), filtros, formato)
        n += 1
    return lst[::-1]

def int_or_0(n):
    """
    Regresa una cadena como su representación en entero positivo.
    Recibe:
        n (str) - cadena con la representación de un entero.
    Regresa:
        int - el entero positivo que representa la cadena.
    """
    try:
        res = int(n)
        return 0 if res < 0 else res
    except:
        return 0

def obten_filtros(request):
    """
    Obtiene los filtros del request indicado.
    Recibe:
        request (django.http.request) - el request
    Regresa:
        list - lista de filtros, cada filtro es una tupla t
            de la forma t = (str, bool)
    """
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
    """
    Vista para la sección de monitoreo de usuarios.
    """
    context = {
        'usuarios_activos' : ejecuta('--usuarios-activos'),
        'usuarios_grupos' : ejecuta('--usuario-grupos'),
        'usuarios_bloqueados' : ejecuta('--usuarios-bloqueados')
    }
    return render(request, 'secciones/monitoreo_usuarios.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_procesos(request):
    """
    Vista para la sección de monitoreo de procesos.
    """
    filtros = obten_filtros(request)
    context = {'salida' : ejecuta('--procesos', filtros=filtros)}
    return render(request, 'secciones/monitoreo_procesos.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_red(request):
    """
    Vista para la sección de monitoreo de red.
    """
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
def monitoreo_almacenamiento(request):
    """
    Vista para la sección de monitoreo de almacenamiento.
    """
    context = {
        'particiones' : ejecuta('--particiones'),
        'memoria' : ejecuta('--memoria'),
        'cpu' : ejecuta('--cpu')
    }
    return render(request, 'secciones/monitoreo_almacenamiento.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_archivos(request):
    """
    Vista para la sección de monitoreo de almacenamiento.
    """
    filtros = obten_filtros(request)
    m = request.GET.get('max')
    max_lineas = int_or_0(m) if m else 100
    context = {'salida' : ejecuta('-f', max_lineas=max_lineas, filtros=filtros)}
    return render(request, 'secciones/monitoreo_archivos.html', context)

@login_required(login_url=reverse_lazy('login'))
def monitoreo_web(request):
    """
    Vista para la sección de monitoreo del servidor web.
    Lee la ubicación de las bitácoras del archivo de configuración
    de la aplicación.
    """
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
    """
    Clase para la sección de monitoreo genérico.
    """
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
    """
    Vista para una bitácora genérica.
    """
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
    """
    Vista para una bitácora de acceso de Apache.
    Obtiene la lista de las bitácoras de acceso de Apache y muestra la
    bitácora que está en la posición indicada (contando desde 1).
    """
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
    """
    Vista para una bitácora de error de Apache.
    Obtiene la lista de las bitácoras de error de Apache y muestra la
    bitácora que está en la posición indicada (contando desde 1).
    """
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
    """
    Muestra las gráficas y estadísticas generadas por goaccess.
    """
    f = open(os.path.join(settings.BASE_DIR, "secciones/templates/secciones/graficas.html"))
    l = f.read()
    f.close()
    return HttpResponse(l)
