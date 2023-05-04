from django.contrib import admin
from .models import Order, Cart, CartItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "talentuser", "number_of_days", "start_date", "slot_of_day", "event_type")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "transaction_id", "total_amount", "is_complete")

    def user(self, obj):
        if obj.generaluser:
            return obj.generaluser.userlink
        else:
            return "-"
