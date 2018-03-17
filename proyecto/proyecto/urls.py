"""proyecto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import index, RegistroUsuario, ListarUsuarios, DetallesUsuario, EditarUsuario, EliminarUsuario
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('usuario/<int:pk>', DetallesUsuario.as_view(), name='usuario'),
    path('usuario/<int:pk>/eliminar', EliminarUsuario.as_view(), name='eliminar-usuario'),
    path('usuarios/', ListarUsuarios.as_view(), name='usuarios'),
    path('editar-datos', EditarUsuario.as_view(), name='editar-datos'),
    path('cambiar_contrasena/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('cambiar_contrasena/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
]
