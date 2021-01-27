#encoding: utf-8
from django.db import models

class Genero(models.Model):
    nombre = models.CharField(max_length=30, verbose_name= 'Género')
    
    def __str__(self):
        return self.nombre
    
class Juego(models.Model):
    titulo = models.TextField(verbose_name='Título')
    #las imágenes de las recetas subidas por los usuarios se almacenan el el directorio 'recetas' dentro
    #del directorio 'carga'. El directorio 'carga' se indica en MEDIA_ROOT (mirar settings.py)
    cover = models.ImageField(upload_to='covers', verbose_name='Carátula')
    cover_path = models.CharField(max_length=200,verbose_name='Carátula')
    description = models.CharField(max_length=500, verbose_name='Descripción')
    release= models.DateField(verbose_name='Fecha de lanzamiento')
    precio = models.DecimalField(max_digits=5,decimal_places=2,verbose_name='Precio')
    generos = models.ManyToManyField(Genero)

    def __str__(self):
        return self.titulo
    