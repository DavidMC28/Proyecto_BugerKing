from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    descripcion = models.TextField()
    ingredientes = models.TextField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    promocion = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    direccion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['usuario__first_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username}"

class Empleado(models.Model):
    PUESTOS = [
        ('GERENTE', 'Gerente'),
        ('CAJERO', 'Cajero'),
        ('COCINERO', 'Cocinero'),
        ('LIMPIEZA', 'Limpieza'),
        ('ATENCION', 'Atención al Cliente'),
    ]
    
    nombre = models.CharField(max_length=200)
    puesto = models.CharField(max_length=20, choices=PUESTOS)
    salario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_contratacion = models.DateField()
    horas_semanales = models.IntegerField(validators=[MinValueValidator(0)])
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    foto = models.ImageField(upload_to='empleados/', null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.puesto}"

class Proveedor(models.Model):
    empresa = models.CharField(max_length=200)
    contacto = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    direccion = models.TextField()
    categoria = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='proveedores/', null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['empresa']
    
    def __str__(self):
        return self.empresa

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    completada = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Venta {self.id} - {self.cliente}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    class Meta:
        ordering = ['venta', 'producto']
    
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    def __str__(self):
        return f"{self.producto} x {self.cantidad}"