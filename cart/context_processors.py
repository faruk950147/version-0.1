from django.shortcuts import redirect, get_object_or_404
from django.db.models import Min, Max
from django.utils import timezone
from cart.models import Cart
from stories.models import (
    Category, Brand, Product, Images, Color, Size, Variants,
)

def get_filters(request):
    cart_products = Cart.objects.filter(user_id=request.user.id)
    
    qty_total_price = sum(cart_product.single_price * cart_product.quantity for cart_product in cart_products)

    return {
        'cart_products': cart_products,
        'qty_total_price': qty_total_price,
        'sub_total': qty_total_price, 
        'finale_price': qty_total_price + 150,
    }
