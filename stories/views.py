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
from cart.forms import CartForm

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
        # Get the product based on the provided id or return a 404 error if not found
        product = get_object_or_404(Product, id=id)

        # Get related products from the same category, excluding the current product
        related_products = Product.objects.filter(category=product.category).exclude(id=id).select_related('category').order_by('-id')[:4]

        # Get active reviews for this product
        reviews = Review.objects.filter(product=product, status=True).select_related('user')

        # Count the total number of reviews for this product
        reviews_total = reviews.count()
        # Prefetch for color and size variants to avoid unnecessary queries
        size_variants = Variants.objects.filter(product=product, size__isnull=False).prefetch_related('size').order_by('size')
        color_variants = Variants.objects.filter(product=product, color__isnull=False).prefetch_related('color').order_by('color')

        # Get unique size variants with associated image URLs
        unique_sizes = {variant.size.id: {'size': variant.size, 'image': variant.image if variant.image else 'default_image_url', 'price': variant.price}for variant in size_variants}

        # Get unique color variants with associated image URLs
        unique_colors = {variant.color.id: {'color': variant.color, 'image': variant.image if variant.image else 'default_image_url', 'price': variant.price} for variant in color_variants}

        context = {
            'product': product,  
            'related_products': related_products,  
            'reviews': reviews,  
            'reviews_total': reviews_total,  
            'unique_sizes': unique_sizes,  
            'unique_colors': unique_colors,
        }
        return render(request, 'stories/single.html', context)

def get_colors_by_size(request):
    size_id = request.GET.get('size_id')
    
    if size_id:
        # Fetch the variants based on the selected size
        variants = Variants.objects.filter(size_id=size_id)
        
        # Collect the color data for each variant
        colors = []
        for variant in variants:
            if variant.color:
                colors.append({
                    'id': variant.color.id,
                    'title': variant.color.title,
                    'code': variant.color.code,
                    'image': variant.image if variant.image else 'default_image_url', 
                    'price': variant.price
                })
        
        return JsonResponse({'colors': colors, 'status': 200, 'messages': 'Colors available for this size'})
    else:
        return JsonResponse({'colors': [], 'status': 400, 'messages': 'Invalid size ID'})  

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