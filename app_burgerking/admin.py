from django.contrib import admin
from .models import *

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'promocion', 'activo']
    list_filter = ['categoria', 'promocion', 'activo']
    search_fields = ['nombre', 'descripcion']
    list_editable = ['precio', 'promocion', 'activo']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'correo', 'fecha_registro']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'correo']

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'puesto', 'salario', 'fecha_contratacion', 'activo']
    list_filter = ['puesto', 'activo']
    search_fields = ['nombre']
    list_editable = ['puesto', 'salario', 'activo']

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'contacto', 'telefono', 'categoria', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['empresa', 'contacto']
    list_editable = ['activo']

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    # QUITAR 'empleado' de list_display
    list_display = ['id', 'fecha', 'cliente', 'total', 'completada']
    
    # QUITAR 'empleado' de list_filter
    list_filter = ['fecha', 'completada']
    
    # QUITAR 'empleado__nombre' de search_fields
    search_fields = ['cliente__usuario__username']
    
    inlines = [DetalleVentaInline]
    list_editable = ['completada']
    
    # OPCIONAL: Si quieres quitar el campo empleado del formulario también
    exclude = ['empleado']