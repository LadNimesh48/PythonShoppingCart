from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price')
    extra = 0

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'payment_id', 'payment_method', 'amount_paid', 'status', 'created_at')
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'payment', 'order_number', 'first_name', 'last_name', 'order_note', 'order_total', 'tax', 'status', 'is_ordered')
    list_filter = ('status', 'is_ordered')
    search_fields = ('order_number', 'first_name', 'last_name', 'order_note', 'email', 'phone')
    list_per_page = 20
    inlines = [OrderProductInline]

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'order', 'payment', 'product', 'ordered')

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
