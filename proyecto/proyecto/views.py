from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistroUsuarioForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeletionMixin, UpdateView
from django.views.generic import CreateView, ListView, DetailView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.conf import settings
import subprocess as sp

def ejecuta(bandera):
    """
    Ejecuta el script de la aplicación con la bandera indicada y regresa la salida.
    """
    p = sp.Popen("%s %s" % (settings.SCRIPT_SECCIONES, bandera), shell=True, stdout=sp.PIPE)
    output = p.stdout.read()
    return output.decode('utf-8')

@login_required(login_url=reverse_lazy('login'))
def index(request):
    """
    Vista para la página de inicio (dashboard).
    """
    context = {
        'datos' : ejecuta("--datos"),
        'cron' : ejecuta("--cron")
    }
    return render(request, 'index.html', context)

class RegistroUsuario(LoginRequiredMixin, CreateView):
    """
    Clase que permite registrar un nuevo usuario.
    """
    
    model = User
    form_class = RegistroUsuarioForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('usuarios')

class ListarUsuarios(LoginRequiredMixin, ListView):
    """
    Clase que permite listar los usuarios en la base de datos.
    """
    model = User
    context_object_name = 'usuarios'
    template_name = 'registration/usuarios.html'

class EditarUsuario(LoginRequiredMixin, UpdateView):
    """
    Clase que permite editar un usuario.
    """
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    template_name = 'registration/editar_usuario.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('usuarios')

    def get_object(self,queryset=None):
        return self.request.user
    
class EliminarUsuario(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Clase que pemrite eliminar un usuario
    """
    model = User
    success_url = reverse_lazy('usuarios')
    success_message = 'Usuario eliminado'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarUsuario, self).delete(request, *args, **kwargs)
