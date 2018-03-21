from django.urls import path
from . import views

urlpatterns = [
    path('nueva', views.NuevaSeccion.as_view(), name='nueva-seccion'),
    path('<slug:slug>/editar', views.EditarSeccion.as_view(), name='editar-seccion'),
    path('<slug:slug>/eliminar', views.EliminarSeccion.as_view(), name='eliminar-seccion'),
    path('', views.ListarSecciones.as_view(), name='administrar-secciones'),
    path('usuarios', views.monitoreo_usuarios, name='monitoreo-usuarios'),
    path('procesos', views.monitoreo_procesos, name='monitoreo-procesos'),
    path('red', views.monitoreo_red, name='monitoreo-red'),
    path('autenticacion', views.monitoreo_autenticacion, name='monitoreo-autenticacion'),
    path('almacenamiento', views.monitoreo_almacenamiento, name='monitoreo-almacenamiento'),
    path('archivos', views.monitoreo_archivos, name='monitoreo-archivos'),
    path('web', views.monitoreo_web, name='monitoreo-web'),
    path('<slug:slug>', views.MonitoreoGenerico.as_view(), name='monitoreo-generico'),
]
