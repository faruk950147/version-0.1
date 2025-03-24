from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from stories.models import Product, Variants

# Custom User model import
User = get_user_model()

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=10, unique=True)
    coupon_discount = models.PositiveIntegerField(default=0)  # Percentage discount
    is_expired = models.BooleanField(default=False)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ['-id']
        verbose_name_plural = '1. Coupons'

    def __str__(self):
        return self.coupon_code

    def is_valid(self, total_amount):
        """Check if the coupon is valid based on expiration and minimum amount."""
        return not self.is_expired and total_amount >= self.minimum_amount


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    variant = models.ForeignKey(Variants, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = '01. Carts'

    @property
    def single_price(self):
        """Return variant price if selected, else product price."""
        return self.variant.price if self.variant else self.product.price

    @property
    def qty_total_price(self):
        """Calculate total price based on quantity."""
        return self.quantity * self.single_price

    @property
    def discount_price(self):
        """Calculate price after coupon discount is applied."""
        if self.coupon and self.coupon.is_valid(self.qty_total_price):
            discount = (self.coupon.coupon_discount / 100) * self.qty_total_price
            return self.qty_total_price - discount
        return self.qty_total_price

    def __str__(self):
        return f"{self.user.username} - {self.product.title} (Qty: {self.quantity})"
