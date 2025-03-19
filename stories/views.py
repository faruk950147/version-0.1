from django.shortcuts import render,redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import generic
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.db.models import Min, Max
import json
from stories.models import (
    Category,Brand,Product, Images,Color,Size,Variants,Slider,Banner,ProductFuture,Review
)
# from cart.forms import CartForm

# Create your views here.
@method_decorator(never_cache, name='dispatch')
class HomeView(generic.View):
    def get(self, request):
        context = {
            'sliders': Slider.objects.filter(status=True).order_by('id'),
            'banners': Banner.objects.filter(status=True).order_by('id')[:3],
            'side_deals_banners': Banner.objects.filter(status=True, side_deals=True, side_deals_is_active=True).order_by('id')[:1],
            'deals_products': Product.objects.filter(offers_deadline__isnull=False,  is_timeline=True, deals=True, status=True).order_by("id")[:6],
            'current_time': timezone.now(),
            'new_collections': Product.objects.filter(status=True, new_collection=True).order_by('id')[:4], 
            'girls_collections': Product.objects.filter(status=True, girls_collection=True).order_by('id')[:4],
            'men_collections': Product.objects.filter(status=True, men_collection=True).order_by('id')[:4],
            'latest_collections': Product.objects.filter(status=True, latest_collection=True).order_by('id')[:4],
            'pick_collections': Product.objects.filter(status=True, pick_collection=True).order_by('id')[:4],  
        }
        return render(request, 'stories/home.html', context)

@method_decorator(never_cache, name='dispatch')
class SingleProductView(generic.View):
    def get(self, request, id):
        product = get_object_or_404(Product, id=id)

        related_products = Product.objects.filter(category=product.category).exclude(id=id).select_related('category').order_by('-id')[:4]

        reviews = Review.objects.filter(product=product, status=True).select_related('user')
        reviews_total = reviews.count()

        size_variants = Variants.objects.filter(product=product, size__isnull=False).select_related('size').order_by('size')
        color_variants = Variants.objects.filter(product=product, color__isnull=False).select_related('color').order_by('color')

        unique_sizes = {
            variant.size.id: {
                'size': variant.size,
                'image': variant.image if variant.image else 'default_image_url',
                'price': variant.price
            } for variant in size_variants
        }

        unique_colors = {
            variant.color.id: {
                'color': variant.color,
                'image': variant.image if variant.image else 'default_image_url',
                'price': variant.price
            } for variant in color_variants
        }

        first_size_variant = size_variants.first()
        first_color_variant = color_variants.first()

        selected_size_title = first_size_variant.size.title if first_size_variant else "Unknown Size"
        selected_color_title = first_color_variant.color.title if first_color_variant else "Unknown Color"

        # Correct price selection logic
        selected_price = None
        if first_color_variant:
            selected_price = first_color_variant.price
        elif first_size_variant:
            selected_price = first_size_variant.price
        else:
            selected_price = product.price

        selected_image_size = first_size_variant.image if first_size_variant else 'default_image_url'
        selected_image_color = first_color_variant.image if first_color_variant else 'default_image_url'

        context = {
            'product': product,
            'related_products': related_products,
            'reviews': reviews,
            'reviews_total': reviews_total,
            'unique_sizes': unique_sizes,
            'unique_colors': unique_colors,
            'selected_size_title': selected_size_title,
            'selected_color_title': selected_color_title,
            'selected_price': selected_price,
            'selected_image_size': selected_image_size,
            'selected_image_color': selected_image_color,
        }
        return render(request, 'stories/single.html', context)

class GetColorsBySize(generic.View):
    def get(self, request):
        size_id = request.GET.get('size_id')
        product_id = request.GET.get('product_id')

        try:
            size_id = int(size_id)
            product_id = int(product_id)
        except (ValueError, TypeError):
            return JsonResponse({'colors': [], 'status': 400, 'messages': 'Invalid size ID or product ID'})

        variants = Variants.objects.filter(product_id=product_id, size_id=size_id).select_related('size', 'color')

        if not variants.exists():
            return JsonResponse({'colors': [], 'status': 404, 'messages': 'No colors available for this size'})

        selected_variant = variants.first()
        selected_size_title = selected_variant.size.title if selected_variant else "Unknown Size"
        selected_price = selected_variant.price if selected_variant else None
        
        colors = [
            {
                'id': variant.color.id,
                'title': variant.color.title,
                'code': variant.color.code,
                'image': variant.image if variant.image else 'default_image_url',
                'price': variant.price
            }
            for variant in variants if variant.color
        ]
        
        return JsonResponse({
            'colors': colors,
            'selected_size_title': selected_size_title,
            'selected_price': selected_price,
            'status': 200,
            'messages': f'Colors available for size {selected_size_title}'})
   
@method_decorator(never_cache, name='dispatch')
class GetPriceByColor(generic.View):
    def get(self, request):
        color_id = request.GET.get('color_id')
        product_id = request.GET.get('product_id')
        print('color_id', color_id, 'product_id', product_id)
        try:
            color_id = int(color_id)
            product_id = int(product_id)
        except (ValueError, TypeError):
            return JsonResponse({'price': None, 'status': 400, 'messages': 'Invalid color ID or product ID'})

        variants = Variants.objects.filter(product_id=product_id, color_id=color_id).select_related('color', 'size')

        if not variants.exists():
            return JsonResponse({'price': None, 'status': 404, 'messages': 'No price available for this color'})

        selected_variant = variants.first()
        selected_color_title = selected_variant.color.title if selected_variant else "Unknown Color"
        selected_price = selected_variant.price if selected_variant else None
        selected_size_title = selected_variant.size.title if selected_variant.size else "Unknown Size"  # ✅ Size যোগ করা হলো
    
        return JsonResponse({
            'selected_color_title': selected_color_title,
            'selected_size_title': selected_size_title,  # ✅ Include size
            'selected_price': selected_price,
            'status': 200,
            'messages': f'Price available for color {selected_color_title}'
        })
     
@method_decorator(never_cache, name='dispatch')
class GetPriceBySize(generic.View):
    def get(self, request):
        size_id = request.GET.get('size_id')
        product_id = request.GET.get('product_id')

        try:
            size_id = int(size_id)
            product_id = int(product_id)
        except (ValueError, TypeError):
            return JsonResponse({'price': None, 'status': 400, 'messages': 'Invalid size ID or product ID'})

        variants = Variants.objects.filter(product_id=product_id, size_id=size_id).select_related('size', 'color')

        if not variants.exists():
            return JsonResponse({'price': None, 'status': 404, 'messages': 'No price available for this size'})

        selected_variant = variants.first()
        selected_size_title = selected_variant.size.title if selected_variant else "Unknown Size"
        selected_price = selected_variant.price if selected_variant else None
    
        return JsonResponse({
            'selected_size_title': selected_size_title,
            'selected_price': selected_price,
            'status': 200,
            'messages': f'Price available for size {selected_size_title}'
        })

@method_decorator(never_cache, name='dispatch')
class ReviewsView(LoginRequiredMixin, generic.View):
    login_url = reverse_lazy('sign')
    def post(self, request):  
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                # Check if updating an existing review
                review_id = data.get("review_id")  
                # Get product ID from request
                product_id = data.get("product_id")  
                # Get the form data
                subject = data.get("subject")
                comment = data.get("comment")
                rate = int(data.get("rate"))
                    
                product = get_object_or_404(Product, id=product_id)  # Ensure product exists
                    
                # Rating validation (1 to 5)
                if not (1 <= rate <= 5):
                    return JsonResponse({"status": 400, "messages": "Invalid rating. Must be between 1 and 5."})

                # Check if the user has already reviewed this product
                if not review_id:
                    existing_review = Review.objects.filter(product=product, user=request.user).first()
                    if existing_review:
                            return JsonResponse({"status": 400, "messages": "You have already reviewed this product."})
                
                if review_id:  # Editing an existing review
                    review = get_object_or_404(Review, id=review_id, user_id=request.user.id)
                    review.subject = subject
                    review.comment = comment
                    review.rate = rate
                    review.save()
                else:  # Creating a new review
                    review = Review()
                    review.product = product
                    review.user_id = request.user.id
                    review.subject = subject
                    review.comment = comment
                    review.rate = rate
                    review.save()
                return JsonResponse({
                    "status": 200,
                    "review_id": review.id,
                    "product_id": review.product.id,
                    "user": review.user.username,
                    "subject": review.subject,
                    "comment": review.comment,
                    "rate": review.rate,  
                    "updated_date": review.updated_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "messages": "Review added successfully"
                })
            except Review.DoesNotExist:
                return JsonResponse({"status": 400, "messages": "Review not found for this user"})
            except Exception as e:
                return JsonResponse({"status": 400, "messages": str(e)})