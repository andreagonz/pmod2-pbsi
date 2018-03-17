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

@login_required(login_url=reverse_lazy('login'))
def index(request):
    return render(request, 'index.html')

class RegistroUsuario(LoginRequiredMixin, CreateView):

    model = User
    form_class = RegistroUsuarioForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('usuarios')

class ListarUsuarios(LoginRequiredMixin, ListView):

    model = User
    context_object_name = 'usuarios'
    template_name = 'registration/usuarios.html'

class DetallesUsuario(LoginRequiredMixin, DetailView):

    model = User
    template_name = 'registration/usuario.html'
    context_object_name = 'usuario'

class EditarUsuario(LoginRequiredMixin, UpdateView):

    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    template_name = 'registration/editar_usuario.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('usuario', kwargs={'pk': self.request.user.pk})

    def get_object(self,queryset=None):
        return self.request.user
    
class EliminarUsuario(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    
    model = User
    success_url = reverse_lazy('usuarios')
    success_message = 'Usuario eliminado'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EliminarUsuario, self).delete(request, *args, **kwargs)
