from .models import CartItem

def cart_count(request):
    """Provides cart count to all templates."""
    if request.user.is_authenticated:
        cart_items_count = sum(item.quantity for item in CartItem.objects.filter(user=request.user))
    else:
        cart_items_count = 0
    return {'cart_items_count': cart_items_count}
