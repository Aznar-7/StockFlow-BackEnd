from django.urls import path
from .views import auth_me, products_list_create, product_detail, movements_list_create, product_reactivate, audit_logs_list
from .auth_views import login


urlpatterns = [
    path("auth/login/", login),

    path('products/', products_list_create),
    path("products/<int:pk>/", product_detail),
    path("movements/", movements_list_create),
    path("products/<int:pk>/reactivate/", product_reactivate),
    path("auth/me/", auth_me),
    
    path("audit-logs/", audit_logs_list),
]