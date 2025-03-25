from django.contrib import admin
from unfold.admin import ModelAdmin
import admin_thumbnails

from cart.models import Cart, Coupon

# Register your models here.
class CouponAdmin(ModelAdmin):
    list_display = ['id', 'coupon_code', 'coupon_discount', 'is_expired', 'minimum_amount']
    search_fields = ['coupon_code']
    list_filter = ['is_expired']
admin.site.register(Coupon, CouponAdmin)

class CartAdmin(ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'single_price', 'qty_total_price', 'discount_price', 'total']
    search_fields = ['user__username', 'product__title']
    list_filter = ['user', 'product', 'quantity']
    readonly_fields = ['single_price', 'qty_total_price', 'discount_price', 'total']
admin.site.register(Cart, CartAdmin)

