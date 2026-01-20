from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Product, StockMovement
from .serializers import (
    ProductSerializer,
    StockMovementSerializer,
    StockMovementReadSerializer,
)



@api_view(["GET", "POST"])
def products_list_create(request):
    if request.method == "GET":
        products = Product.objects.filter(is_active=True).order_by("id")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    if request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = ProductSerializer(product, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        product.is_active = False
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def movements_list_create(request):
    # -------- GET: listar movimientos --------
    if request.method == "GET":
        qs = StockMovement.objects.select_related("product").order_by("-id")

        product_id = request.query_params.get("product")
        mtype = request.query_params.get("type")

        if product_id:
            qs = qs.filter(product_id=product_id)
        if mtype:
            qs = qs.filter(movement_type=mtype)

        serializer = StockMovementReadSerializer(qs, many=True)
        return Response(serializer.data)

    # -------- POST: crear movimiento (ATÓMICO) --------
    serializer = StockMovementSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    product_id = serializer.validated_data["product"].id
    movement_type = serializer.validated_data["movement_type"]
    quantity = serializer.validated_data["quantity"]

    if quantity < 0:
        return Response({"error": "quantity debe ser >= 0"}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        product = Product.objects.select_for_update().get(id=product_id)

        if not product.is_active:
            return Response({"error": "Producto inactivo"}, status=status.HTTP_400_BAD_REQUEST)

        if movement_type == "IN":
            new_stock = product.stock + quantity

        elif movement_type == "OUT":
            if product.stock - quantity < 0:
                return Response({"error": "Stock insuficiente"}, status=status.HTTP_400_BAD_REQUEST)
            new_stock = product.stock - quantity

        elif movement_type == "ADJUST":
            new_stock = quantity

        else:
            return Response({"error": "movement_type inválido"}, status=status.HTTP_400_BAD_REQUEST)

        movement = serializer.save()
        product.stock = new_stock
        product.save()

    return Response(StockMovementReadSerializer(movement).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def product_reactivate(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = True
    product.save()
    return Response(ProductSerializer(product).data)


def get_role(user):
    # prioridad: admin > operator > viewer
    if user.is_superuser or user.is_staff:
        return "admin"
    if user.groups.filter(name="operator").exists():
        return "operator"
    if user.groups.filter(name="viewer").exists():
        return "viewer"
    return "viewer"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def auth_me(request):
    user = request.user
    return Response({
        "username": user.username,
        "role": get_role(user),
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    })

