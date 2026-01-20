from django.contrib import admin
from .models import Product, StockMovement

# Register your models here.

admin.site.register(StockMovement)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "sku", "name", "category", "stock", "min_stock", "location", "unit_price", "is_active")
    search_fields = ("sku", "name", "category", "location")
    list_filter = ("category", "is_active")
