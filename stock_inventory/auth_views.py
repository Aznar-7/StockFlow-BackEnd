from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Credenciales inválidas"}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        "token": token.key,
        "username": user.username,
    })
