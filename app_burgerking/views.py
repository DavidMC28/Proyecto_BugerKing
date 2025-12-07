from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import *
from .forms import *
import json

def es_administrador(user):
    return user.is_staff

# Vistas de autenticación - CORREGIDA
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # DEBUG: Verificar tipo de usuario
            print(f"🔍 DEBUG LOGIN - Usuario: {user.username}, is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")
            
            messages.success(request, f'¡Bienvenido {user.username}!')
            
            # VERIFICACIÓN CORREGIDA - Solo verificar is_staff
            if user.is_staff:
                print("🎯 REDIRIGIENDO A ADMIN_PRODUCTOS")
                return redirect('admin_productos')  # Administradores
            else:
                print("👤 REDIRIGIENDO A INICIO (Cliente)")
                # PARA CLIENTES: usar el parámetro next o ir al inicio
                next_url = request.POST.get('next', 'inicio')
                if next_url and next_url != 'inicio':
                    return redirect(next_url)
                else:
                    return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    # Pasar el parámetro next al contexto del template
    context = {
        'next': request.GET.get('next', '')
    }
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente')
    return redirect('inicio')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear perfil de cliente
            Cliente.objects.create(
                usuario=user,
                telefono='',
                correo=user.email,
                direccion=''
            )
            
            messages.success(request, '¡Cuenta creada exitosamente! Por favor inicia sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    
    return render(request, 'register.html', {'form': form})

# Vistas públicas
def inicio(request):
    productos_destacados = Producto.objects.filter(activo=True, promocion=True)[:6]
    return render(request, 'inicio.html', {'productos_destacados': productos_destacados})

def menu(request):
    categorias = Categoria.objects.all()
    categoria_seleccionada = request.GET.get('categoria')
    
    if categoria_seleccionada:
        productos = Producto.objects.filter(categoria__id=categoria_seleccionada, activo=True)
    else:
        productos = Producto.objects.filter(activo=True)
    
    return render(request, 'menu.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada
    })

def promociones(request):
    productos_promocion = Producto.objects.filter(promocion=True, activo=True).order_by('precio')
    return render(request, 'promociones.html', {'productos': productos_promocion})

def contacto(request):
    return render(request, 'contacto.html')

def novedades(request):
    productos_aleatorios = Producto.objects.filter(activo=True).order_by('?')[:8]
    return render(request, 'novedades.html', {'productos': productos_aleatorios})

# Vistas de carrito
@login_required
def carrito(request):
    carrito_data = request.session.get('carrito', {})
    items = []
    total = 0
    
    for producto_id, item_data in carrito_data.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            subtotal = producto.precio * item_data['cantidad']
            total += subtotal
            
            items.append({
                'id': producto_id,
                'producto': producto,
                'cantidad': item_data['cantidad'],
                'subtotal': subtotal
            })
        except Producto.DoesNotExist:
            continue
    
    return render(request, 'carrito.html', {'items': items, 'total': total})

@login_required
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    carrito = request.session.get('carrito', {})
    
    if str(producto_id) in carrito:
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        carrito[str(producto_id)] = {
            'cantidad': 1,
            'nombre': producto.nombre,
            'precio': str(producto.precio)
        }
    
    request.session['carrito'] = carrito
    messages.success(request, f'{producto.nombre} agregado al carrito')
    
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'carrito_count': len(carrito)})
    
    return redirect('menu')

@login_required
def eliminar_carrito(request, item_id):
    carrito = request.session.get('carrito', {})
    
    if str(item_id) in carrito:
        del carrito[str(item_id)]
        request.session['carrito'] = carrito
        messages.success(request, 'Producto eliminado del carrito')
    
    return redirect('carrito')

@login_required
def actualizar_carrito(request, item_id):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = request.session.get('carrito', {})
        
        if str(item_id) in carrito and cantidad > 0:
            carrito[str(item_id)]['cantidad'] = cantidad
            request.session['carrito'] = carrito
        
        return redirect('carrito')

@login_required
def checkout(request):
    # Obtener datos del carrito para mostrar en el resumen
    carrito_data = request.session.get('carrito', {})
    items = []
    total = 0
    
    for producto_id, item_data in carrito_data.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            subtotal = producto.precio * item_data['cantidad']
            total += subtotal
            
            items.append({
                'id': producto_id,
                'producto': producto,
                'cantidad': item_data['cantidad'],
                'subtotal': subtotal
            })
        except Producto.DoesNotExist:
            continue
    
    # Obtener información del cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        cliente = None

    if request.method == 'POST':
        if not carrito_data:
            messages.error(request, 'El carrito está vacío')
            return redirect('carrito')
        
        try:
            # Obtener un empleado activo (por ejemplo, el primero)
            empleado = Empleado.objects.filter(activo=True).first()
            
            if not empleado:
                messages.error(request, 'No hay empleados disponibles')
                return redirect('carrito')
            
            # Crear venta
            venta = Venta.objects.create(
                total=total,
                cliente=cliente,
                empleado=empleado,
                completada=True
            )
            
            # Crear detalles de venta
            for producto_id, item_data in carrito_data.items():
                producto = Producto.objects.get(id=producto_id)
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=item_data['cantidad'],
                    precio_unitario=producto.precio
                )
            
            # Limpiar carrito
            request.session['carrito'] = {}
            messages.success(request, '¡Compra realizada exitosamente!')
            return redirect('inicio')
            
        except Exception as e:
            messages.error(request, f'Error al procesar la compra: {str(e)}')
            return redirect('carrito')
    
    # Pasar los datos al template en el método GET
    return render(request, 'checkout.html', {
        'items': items,
        'total': total,
        'cliente': cliente
    })

# Vistas de perfil
@login_required
def perfil_cliente(request):
    cliente = get_object_or_404(Cliente, usuario=request.user)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        user_form = UserForm(request.POST, instance=request.user)
        
        if form.is_valid() and user_form.is_valid():
            user_form.save()
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('perfil_cliente')
    else:
        form = ClienteForm(instance=cliente)
        user_form = UserForm(instance=request.user)
    
    return render(request, 'perfil_cliente.html', {
        'form': form,
        'user_form': user_form,
        'cliente': cliente
    })

# Vistas de administración
@login_required
@user_passes_test(es_administrador)
def admin_productos(request):
    productos = Producto.objects.all()
    return render(request, 'admin/productos.html', {'productos': productos})

@login_required
@user_passes_test(es_administrador)
def admin_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'admin/ventas.html', {'ventas': ventas})

@login_required
@user_passes_test(es_administrador)
def admin_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'admin/clientes.html', {'clientes': clientes})

@login_required
@user_passes_test(es_administrador)
def admin_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'admin/empleados.html', {'empleados': empleados})

@login_required
@user_passes_test(es_administrador)
def admin_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'admin/proveedores.html', {'proveedores': proveedores})

# VISTAS DE CATEGORÍAS - AGREGADAS
@login_required
@user_passes_test(es_administrador)
def admin_categorias(request):
    categorias = Categoria.objects.all()
    return render(request, 'admin/categorias.html', {'categorias': categorias})

@login_required
@user_passes_test(es_administrador)
def agregar_categoria(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        if nombre:
            Categoria.objects.create(nombre=nombre)
            messages.success(request, 'Categoría agregada correctamente')
            return redirect('admin_categorias')
        else:
            messages.error(request, 'El nombre de la categoría es requerido')
    return render(request, 'admin/agregar_categoria.html')

@login_required
@user_passes_test(es_administrador)
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente')
        return redirect('admin_categorias')
    return render(request, 'admin/eliminar_categoria.html', {'categoria': categoria})

# CRUD Productos
@login_required
@user_passes_test(es_administrador)
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente')
            return redirect('admin_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'admin/agregar_producto.html', {'form': form})

@login_required
@user_passes_test(es_administrador)
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente')
            return redirect('admin_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'admin/editar_producto.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(es_administrador)
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado correctamente')
        return redirect('admin_productos')
    
    return render(request, 'admin/eliminar_producto.html', {'producto': producto})

# CRUD Empleados - AGREGADO
@login_required
@user_passes_test(es_administrador)
def agregar_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado agregado correctamente')
            return redirect('admin_empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'admin/agregar_empleado.html', {'form': form})

@login_required
@user_passes_test(es_administrador)
def editar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado correctamente')
            return redirect('admin_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'admin/editar_empleado.html', {'form': form, 'empleado': empleado})

@login_required
@user_passes_test(es_administrador)
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado correctamente')
        return redirect('admin_empleados')
    return render(request, 'admin/eliminar_empleado.html', {'empleado': empleado})

# CRUD Proveedores - AGREGADO
@login_required
@user_passes_test(es_administrador)
def agregar_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor agregado correctamente')
            return redirect('admin_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'admin/agregar_proveedor.html', {'form': form})

@login_required
@user_passes_test(es_administrador)
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, request.FILES, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado correctamente')
            return redirect('admin_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'admin/editar_proveedor.html', {'form': form, 'proveedor': proveedor})

@login_required
@user_passes_test(es_administrador)
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado correctamente')
        return redirect('admin_proveedores')
    return render(request, 'admin/eliminar_proveedor.html', {'proveedor': proveedor})