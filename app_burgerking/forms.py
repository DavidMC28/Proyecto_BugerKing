from django import forms
from django.contrib.auth.models import User
from .models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['telefono', 'correo', 'direccion']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'ingredientes': forms.Textarea(attrs={'rows': 3}),
        }

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }