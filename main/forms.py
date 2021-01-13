# -*- encoding: utf-8 -*-
from django import forms

class UserForm(forms.Form):
    id = forms.CharField(label='User ID')
    
class BusquedaPorTituloForm(forms.Form):
    titulo = forms.CharField(label='Titulo de Juego')