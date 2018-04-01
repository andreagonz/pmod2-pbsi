from django.contrib import admin
from django.urls import path, include
from .views import index, RegistroUsuario, ListarUsuarios, EditarUsuario, EliminarUsuario
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', index, name='index'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),
    path('registro/', RegistroUsuario.as_view(), name='registro'),
    path('usuarios/<int:pk>/eliminar', EliminarUsuario.as_view(), name='eliminar-usuario'),
    path('usuarios/', ListarUsuarios.as_view(), name='usuarios'),
    path('editar-datos', EditarUsuario.as_view(), name='editar-datos'),
    path('cambiar_contrasena/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('cambiar_contrasena/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('secciones/', include('secciones.urls')),
]
