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

# Create your views here.@method_decorator(never_cache, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class AddToCart(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign')
    def post(self, request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                product_id = data.get("product_id")
                size_id = int(data.get("size_id"))
                color_id = int(data.get("color_id"))
                quantity = int(data.get("quantity"))

                # Find the product and variant
                product = get_object_or_404(Product, id=product_id)
                variant = Variants.objects.filter(product=product, size_id=size_id, color_id=color_id).first()

                # Check if variant exists, and if not, check product stock
                if not variant and product.in_stock_max <= 0:
                    return JsonResponse({"status": 400, "messages": "Product is out of stock!"})

                max_stock = variant.quantity if variant else product.in_stock_max

                # Check if the quantity is valid
                if quantity <= 0:
                    return JsonResponse({"status": 400, "messages": "Quantity must be greater than 0!"})

                # If the product already exists in the cart
                existing_cart_item = Cart.objects.filter(user=request.user, product=product, variant=variant if variant else None).first()

                if existing_cart_item:
                    # Check if the previous quantity + new quantity <= stock
                    new_quantity = existing_cart_item.quantity + quantity
                    if new_quantity <= 0:
                        return JsonResponse({"status": 400, "messages": "Quantity cannot be zero or negative!"})

                    if new_quantity <= max_stock:
                        existing_cart_item.quantity = new_quantity
                        existing_cart_item.save()
                        message = "Quantity updated successfully!"
                    else:
                        return JsonResponse({"status": 400, "messages": f"Cannot add more than {max_stock} units!"})
                else:
                    if quantity <= max_stock:
                        Cart.objects.create(user=request.user, product=product, variant=variant, quantity=quantity)
                        message = "Product added to cart successfully!"
                    else:
                        return JsonResponse({"status": 400, "messages": f"Cannot add more than {max_stock} units!"})

                return JsonResponse({
                    'status': 200,
                    'messages': message
                })

            except Exception as e:
                return JsonResponse({'status': 400, 'messages': f"Error: {str(e)}"})

        return JsonResponse({'status': 400, 'messages': 'Invalid request'})

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

                # Find the product in the cart
                cart_product = get_object_or_404(Cart, id=cart_item_id, user=request.user.id)

                # Determine the maximum stock limit
                max_stock = cart_product.variant.quantity if cart_product.variant else cart_product.product.in_stock_max

                # Check the action and update the quantity accordingly
                if action == "increase":
                    if cart_product.quantity < max_stock:
                        cart_product.quantity += 1
                    else:
                        return JsonResponse({'status': 400, 'messages': f"Cannot add more than {max_stock} units of this product!", 'quantity': cart_product.quantity})

                elif action == "decrease":
                    if cart_product.quantity > 1:
                        cart_product.quantity -= 1
                    else:
                        return JsonResponse({'status': 400, 'messages': "Quantity cannot be less than 1!", 'quantity': cart_product.quantity})

                # Save to the database
                cart_product.save()

                # Load all cart items for the user
                cart_products = Cart.objects.filter(user=request.user.id)

                # Calculate the total price of the cart
                cart_total = sum(item.quantity * item.single_price for item in cart_products)
                final_price = cart_total + 150  # Delivery charge 150

                return JsonResponse({
                    "status": 200,
                    "messages": f"Quantity updated successfully! {cart_product.quantity}",
                    "quantity": cart_product.quantity,
                    "cart_total": cart_total,
                    "qty_total_price": cart_product.single_price * cart_product.quantity,  # To keep the variant price
                    "sub_total": cart_total,
                    "finale_price": final_price,
                    "id": cart_item_id
                })

            except Exception as e:
                return JsonResponse({"status": 400, "messages": str(e)})
        return JsonResponse({"status": 400, "messages": "Invalid request"})

@method_decorator(never_cache, name='dispatch')
class RemoveToCart(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign')
    def post(self, request):
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                cart_item_id = data.get("id")

                # Find the cart item
                cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)

                # Calculate the total price of the product (including variant price)
                qty_total_price = cart_item.qty_total_price  # This can be used for the total price of the item

                # Delete the cart item
                cart_item.delete()

                # Load all cart items for the user
                cart_products = Cart.objects.filter(user=request.user)

                # Calculate the total price of the cart
                cart_total = sum(item.quantity * item.single_price for item in cart_products)
                final_price = cart_total + 150  # Delivery charge 150

                return JsonResponse({
                    "status": 200,
                    "messages": "Product removed successfully!",
                    "cart_total": cart_total,
                    "qty_total_price": qty_total_price,  # Price of the item that was removed
                    "sub_total": cart_total,  # Subtotal after removing the item
                    "finale_price": final_price,  # Final price after adding delivery charge
                    "id": cart_item_id  # Returning the id of the removed item
                })

            except Exception as e:
                return JsonResponse({"status": 400, "messages": str(e)})
        return JsonResponse({"status": 400, "messages": "Invalid request"})
