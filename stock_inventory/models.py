from django.db import models

# Create your models here.

# Creamos el modelo de la tabla
class Product(models.Model):
    sku = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=60, blank=True)
    unit = models.CharField(max_length=10, default="u")  # u, kg, lt, etc.
    stock = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=0)
    location = models.CharField(max_length=60, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sku} - {self.name}"
    

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ("IN", "Ingreso"),
        ("OUT", "Egreso"),
        ("ADJUST", "Ajuste"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="movements"
    )

    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=120, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movement_type} {self.quantity} - {self.product.sku}"