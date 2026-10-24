from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'currency', 'status', 'payment_method', 'razorpay_payment_id', 'created_at')
    list_filter = ('status', 'payment_method', 'currency')
    search_fields = ('transaction_id', 'user__email', 'razorpay_payment_id', 'razorpay_order_id')
