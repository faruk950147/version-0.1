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
            'sliders': Slider.objects.filter(status=True).select_related('product').prefetch_related('product__product_variants').order_by('id'),
            'banners': Banner.objects.filter(status=True).select_related('product').prefetch_related('product__product_variants').order_by('id')[:3],
            'side_deals_banners': Banner.objects.filter(status=True, side_deals=True, side_deals_is_active=True).select_related('product').prefetch_related('product__product_variants').order_by('id')[:1],
            'deals_products': Product.objects.filter(offers_deadline__isnull=False,  is_timeline=True, deals=True, status=True).select_related('category', 'brand').prefetch_related('product_variants').order_by("id")[:6],
            'current_time': timezone.now(),
            'new_collections': Product.objects.filter(status=True, new_collection=True).select_related('category', 'brand').prefetch_related('product_variants__color', 'product_variants__size').order_by('id')[:4],
            'girls_collections': Product.objects.filter(status=True, girls_collection=True).select_related('category', 'brand').prefetch_related('product_variants__color', 'product_variants__size').order_by('id')[:4],
            'men_collections': Product.objects.filter(status=True, men_collection=True).select_related('category', 'brand').prefetch_related('product_variants__color', 'product_variants__size').order_by('id')[:4],
            'latest_collections': Product.objects.filter(status=True, latest_collection=True).select_related('category', 'brand').prefetch_related('product_variants__color', 'product_variants__size').order_by('id')[:4],
            'pick_collections': Product.objects.filter(status=True, pick_collection=True).select_related('category', 'brand').prefetch_related('product_variants__color', 'product_variants__size').order_by('id')[:4],   
        }
        return render(request, 'stories/home.html', context)

@method_decorator(never_cache, name='dispatch')
class SingleProductView(generic.View):
    def get(self, request, id):
        product = get_object_or_404(Product.objects.prefetch_related('product_variants'), id=id)

        related_products = Product.objects.filter(category=product.category).exclude(id=product.id).select_related('category').prefetch_related('product_variants__color', 'product_variants__size').order_by('-id')[:4]

        reviews = Review.objects.filter(product=product, status=True).select_related('user').prefetch_related('product')
        reviews_total = reviews.count()

        variants = Variants.objects.filter(product=product).select_related('size', 'color')

        size_variants = variants.filter(size__isnull=False).order_by('size')
        color_variants = variants.filter(color__isnull=False).order_by('color')

        unique_sizes = {variant.size.id: {'size': variant.size, 'image': variant.image or 'No Image Available', 'price': variant.price} for variant in size_variants}
        unique_colors = {variant.color.id: {'color': variant.color, 'image': variant.image or 'No Image Available', 'price': variant.price} for variant in color_variants}

        first_size_variant = size_variants.first()
        first_color_variant = color_variants.first()

        selected_size_id = first_size_variant.size_id if first_size_variant and first_size_variant.size else None
        selected_color_id = first_color_variant.color_id if first_color_variant and first_color_variant.color else None

        selected_size_title = first_size_variant.size.title if first_size_variant and first_size_variant.size else "Unknown Size"
        selected_color_title = first_color_variant.color.title if first_color_variant and first_color_variant.color else "Unknown Color"
        selected_price = first_size_variant.price if first_size_variant else None

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
            'selected_size_id': selected_size_id,
            'selected_color_id': selected_color_id,
        }
        return render(request, 'stories/single.html', context)

@method_decorator(never_cache, name='dispatch')
class GetColorsBySize(generic.View):
    def get(self, request):
        size_id = request.GET.get('size_id')
        product_id = request.GET.get('product_id')

        # Validate input parameters
        if not product_id:
            return JsonResponse({'status': 400, 'messages': 'Product ID is required'}, status=400)

        try:
            size_id = int(size_id) if size_id else None
            product_id = int(product_id)
        except (ValueError, TypeError):
            return JsonResponse({'status': 400, 'messages': 'Invalid size ID or product ID'}, status=400)

        # Query variants based on the provided size_id and product_id
        filter_conditions = {'product_id': product_id}
        if size_id:
            filter_conditions['size_id'] = size_id

        variants = Variants.objects.filter(**filter_conditions).select_related('size', 'color')

        # Build the colors list from the variants
        colors = [
            {
                'id': getattr(variant.color, 'id', None),
                'title': getattr(variant.color, 'title', 'Unknown Color'),
                'code': getattr(variant.color, 'code', '#000000'),
                'image': variant.image or 'No Image Available',
                'price': variant.price
            }
            for variant in variants if variant.color
        ]

        # Handle default values for size and color
        if variants:
            selected_size_title = variants[0].size.title if size_id else "Unknown Size"
            selected_price = variants[0].price if size_id else None
            selected_color_title = colors[0]['title'] if colors else "Unknown Color"
            selected_color_id = colors[0]['id'] if colors else None
        else:
            selected_size_title = "Unknown Size"
            selected_color_title = "Unknown Color"
            selected_price = None
            selected_color_id = None

        # Prepare response message and status code
        if colors:
            message = f'Colors available for size {selected_size_title}' if size_id else 'Only colors available'
            status = 200
        elif size_id:
            message = f'Only size available: {selected_size_title}'
            status = 200
        else:
            message = "No colors available"
            status = 404

        # Return JSON response with the colors and selected attributes
        return JsonResponse({
            'colors': colors,
            'selected_size_title': selected_size_title,
            'selected_price': selected_price,
            'selected_color_title': selected_color_title,
            'selected_size_id': size_id,
            'selected_color_id': selected_color_id,
            'status': status,
            'messages': message
        }, status=status)
    
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