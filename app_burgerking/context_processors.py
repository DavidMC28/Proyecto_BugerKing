def carrito_context(request):
    carrito = request.session.get('carrito', {})
    carrito_count = sum(item['cantidad'] for item in carrito.values())
    return {
        'carrito_count': carrito_count
    }