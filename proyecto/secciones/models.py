from django.db import models

class Seccion(models.Model):

    titulo = models.CharField(max_length=512)
    fecha_creacion = models.DateTimeField(editable=False, auto_now_add=True)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('secciones:seccion', kwargs={'pk': self.pk})
