from django.shortcuts import redirect, get_object_or_404
from django.db.models import Min, Max
from django.utils import timezone
from cart.models import Cart
from stories.models import (
    Category, Brand, Product, Images, Color, Size, Variants,
)

def get_filters(request):
    cart_products = Cart.objects.filter(user=request.user)
    cart_count = cart_products.count()
    # if discount price is less than qty_total_price then use discount_price otherwise use qty_total_price
    qty_total_price = sum(cart_product.discount_price if cart_product.discount_price < cart_product.qty_total_price else cart_product.qty_total_price for cart_product in cart_products)

    return {
        'cart_products': cart_products,
        'cart_count': cart_count,
        'qty_total_price': qty_total_price,  
        'sub_total': qty_total_price,  
        'finale_price': qty_total_price + 150,  
    }

