from django.forms import ModelForm
from .models import Seccion
from django.utils.translation import ugettext_lazy as _

class SeccionForm(ModelForm):

    class Meta:
        model = Seccion
        fields = ['titulo', 'slug']
        labels = {
            'titulo' : _('Título'),
            'slug' : _('Nombre de configuración')
        }
