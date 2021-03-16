# -*- encoding: utf-8 -*-
from django import forms
from main.models import Genero

class UserForm(forms.Form):
    id = forms.CharField(label='User ID')
    
class BusquedaPorTituloForm(forms.Form):
    titulo = forms.CharField(label='Titulo de Juego')

class BusquedaPorGeneroForm(forms.Form):
    lista=[(g.id,g.nombre) for g in Genero.objects.all()]
    genero = forms.MultipleChoiceField(label="Seleccione el/los género/s", choices=lista)
    
class BusquedaPorFechaForm(forms.Form):
    fecha_inicio = forms.DateField(label="Fecha Inicio(Formato dd/mm/yyyy)", widget=forms.DateInput(format='%d/%m/%Y'), required=True)
    fecha_fin = forms.DateField(label="Fecha Fin(Formato dd/mm/yyyy)", widget=forms.DateInput(format='%d/%m/%Y'), required=True)