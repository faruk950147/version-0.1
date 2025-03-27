from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.db.models import Sum
from stories.models import Product, Variants

# Custom User model import
User = get_user_model()

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10, unique=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00')) 
    is_expired = models.BooleanField(default=False)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['id']
        verbose_name_plural = '01. Coupons'

    def __str__(self):
        return self.coupon_code

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    variant = models.ForeignKey(Variants, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['id']
        verbose_name_plural = '02. Carts'

    @property
    def single_price(self):
        """Returns the price of the variant if available; otherwise, returns the base product price."""
        return self.variant.price if self.variant else self.product.price

    @property
    def qty_total_price(self):
        """Calculates the total price based on unit price and quantity."""
        return self.quantity * self.single_price  # `self.single_price` is already a Decimal

    @property
    def discount_price(self):
        """Calculate price after coupon discount is applied."""
 
        return 

    @property
    def total(self):
        """Calculate the total price of all products in the user's cart."""
        carts = Cart.objects.filter(user=self.user)
        total = sum(cart.qty_total_price for cart in carts)  # Sum using a Python generator expression
        return total
    
    def __str__(self):
        variant_info = f" - {self.variant.title}" if self.variant else ""
        return f"{self.user.username} - {self.product.title}{variant_info} (Qty: {self.quantity})"
