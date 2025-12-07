from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # Páginas principales
    path('', views.inicio, name='inicio'),
    path('menu/', views.menu, name='menu'),
    path('promociones/', views.promociones, name='promociones'),
    path('contacto/', views.contacto, name='contacto'),
    path('novedades/', views.novedades, name='novedades'),
    
    # Carrito de compras
    path('carrito/', views.carrito, name='carrito'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('eliminar-carrito/<int:item_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('actualizar-carrito/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Perfil de cliente
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    
    # Admin views (solo para staff)
    path('manager/productos/', views.admin_productos, name='admin_productos'),
    path('manager/ventas/', views.admin_ventas, name='admin_ventas'),
    path('manager/clientes/', views.admin_clientes, name='admin_clientes'),
    path('manager/empleados/', views.admin_empleados, name='admin_empleados'),
    path('manager/proveedores/', views.admin_proveedores, name='admin_proveedores'),
    path('manager/categorias/', views.admin_categorias, name='admin_categorias'),
    
    # CRUD operations
    path('manager/productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('manager/productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('manager/productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    
    # CRUD Categorías
    path('manager/categorias/agregar/', views.agregar_categoria, name='agregar_categoria'),
    path('manager/categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # CRUD Empleados - ✅ AGREGADO
    path('manager/empleados/agregar/', views.agregar_empleado, name='agregar_empleado'),
    path('manager/empleados/editar/<int:pk>/', views.editar_empleado, name='editar_empleado'),
    path('manager/empleados/eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),
    
    # CRUD Proveedores - ✅ AGREGADO
    path('manager/proveedores/agregar/', views.agregar_proveedor, name='agregar_proveedor'),
    path('manager/proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('manager/proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
]