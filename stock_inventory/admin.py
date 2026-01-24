from django.contrib import admin
from .models import Product, StockMovement, AuditLog

# Register your models here.

admin.site.register(StockMovement)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "sku", "name", "category", "stock", "min_stock", "location", "unit_price", "is_active")
    search_fields = ("sku", "name", "category", "location")
    list_filter = ("category", "is_active")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "model_name", "ip_address")
    list_filter = ("action", "model_name")
    search_fields = ("description", "user__username")
    readonly_fields = ("created_at", "user", "action", "model_name", "description", "ip_address")
    
    def has_add_permission(self, request):
        return False # Los logs no deben crearse manualmente
    
    def has_change_permission(self, request, obj=None):
        return False # Los logs no deben editarse
