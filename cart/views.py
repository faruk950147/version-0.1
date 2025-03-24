from django.shortcuts import render,redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import generic
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db.models import Min, Max
import json
from cart.forms import (
    CartForm
)
from stories.models import (
    Product, Variants
)
from cart.models import (
    Cart
)

# Create your views here.
@method_decorator(never_cache, name='dispatch')
class AddTtoCart(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign')
    def post(self, request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                product_id = data.get("product_id")
                size_id = data.get("size_id")
                color_id = data.get("color_id")
                quantity = data.get("quantity")
                product = Product.objects.get(id=product_id)    
                variant = Variants.objects.filter(product=product, size_id=size_id, color_id=color_id).first()
                Cart.objects.create(user=request.user, product=product, variant=variant, quantity=quantity)
                return JsonResponse({
                    'status': 200,
                    'messages': 'Item added to cart successfully!'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 400,
                    'message': str(e)
                })
        return JsonResponse({
            'status': 400,
            'message': 'Invalid request method.'
        })  
        

@method_decorator(never_cache, name='dispatch')
class CartView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign')
    def get(self, request):
        context = {
                
        }
        return render(request, 'cart/cart.html', context)
    
@method_decorator(never_cache, name='dispatch')
class QuantityIncDec(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign')
    def post(self, request):
        if request.method == "POST": 
            try:
                data = json.loads(request.body)
                cart_item_id = data.get("id")
                action = data.get("action")
                # get cart product
                cart_product = get_object_or_404(Cart, id=cart_item_id, user=request.user.id)

                # maximum stock check
                max_stock = cart_product.product.in_stock_max  

                # action update quantity
                if action == "increase":
                    if cart_product.quantity < max_stock:
                        cart_product.quantity += 1
                    else:
                        return JsonResponse({"status": 400, "messages": f"Cannot add more than {max_stock} units of this product!", "quantity": cart_product.quantity})
                elif action == "decrease":
                    if cart_product.quantity > 1:
                        cart_product.quantity -= 1
                    else:
                        return JsonResponse({"status": 400,"messages": "Quantity cannot be less than 1!","quantity": cart_product.quantity})
                # save cart product
                cart_product.save()

                # cart products load (once Query will be)
                cart_products = list(Cart.objects.filter(user=request.user.id))
                cart_total = sum(item.quantity * item.product.price for item in cart_products)
                final_price = cart_total + 150  # delivery charge 150

                return JsonResponse({
                    "status": 200,
                    "messages": f"Quantity updated successfully! {cart_product.quantity}",
                    "quantity": cart_product.quantity,
                    "cart_total": cart_total,
                    "qty_total_price": cart_product.product.price * cart_product.quantity,
                    "sub_total": cart_total,
                    "finale_price": final_price,
                    "id": cart_item_id
                })

            except Exception as e:
                return JsonResponse({"status": 400, "messages": str(e)})
        return JsonResponse({"status": 402, "messages": "Something is happen"})


@method_decorator(never_cache, name='dispatch')
class RemoveToCart(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign')
    def post(self, request):
        if request.method == "POST": 
            try:
                data = json.loads(request.body)
                cart_item_id = data.get("id")

                # get cart item
                cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)

                # qty total price
                qty_total_price = cart_item.product.price * cart_item.quantity

                # delete cart item
                cart_item.delete()

                # cart products load (once Query will be)
                cart_products = list(Cart.objects.filter(user=request.user))
                cart_total = sum(item.quantity * item.product.price for item in cart_products)
                final_price = cart_total + 150  # delivery charge 150

                return JsonResponse({
                    "status": 200,
                    "messages": "Product removed successfully!",
                    "cart_total": cart_total,
                    "qty_total_price": qty_total_price,
                    "sub_total": cart_total,
                    "finale_price": final_price,
                    "id": cart_item_id
                })

            except Exception as e:
                return JsonResponse({"status": 400, "messages": str(e)})
        return JsonResponse({"status": 400, "messages": "Invalid request"})
