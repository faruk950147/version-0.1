from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from cart.views import (
    AddToCart, CartView, QuantityIncDec, RemoveToCart
)
urlpatterns = [
    path('addtocart/', AddToCart.as_view(), name='addtocart'),
    path('cartview/', CartView.as_view(), name='cartview'),
    path("qtyincdec/", csrf_exempt(QuantityIncDec.as_view()), name="qtyincdec"),
    path('removetocart/', csrf_exempt(RemoveToCart.as_view()), name="removetocart")
]