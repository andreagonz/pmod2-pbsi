from django import template
from secciones.models import Seccion

register = template.Library()

@register.filter(name='addclass')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.simple_tag
def lista_secciones():
    return Seccion.objects.all()
