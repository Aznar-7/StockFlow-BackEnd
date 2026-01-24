from django.apps import AppConfig


class StockInventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stock_inventory'

    def ready(self):
        import stock_inventory.signals  # Conectamos las señales
