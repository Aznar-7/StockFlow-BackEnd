from django.urls import path
from .views import products_list_create, product_detail, movements_list_create, product_reactivate
from .auth_views import login


urlpatterns = [
    path("auth/login/", login),

    path('products/', products_list_create),
    path("products/<int:pk>/", product_detail),
    path("movements/", movements_list_create),
    path("products/<int:pk>/reactivate/", product_reactivate),

]