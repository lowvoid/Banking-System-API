from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer
from core.utils import api_response


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return api_response( data={ "user": UserSerializer(user).data, "refresh": str(refresh), "access": str(refresh.access_token)}, message="User created successfully", success=True, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return api_response(message="Refresh token is required", success=False, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return api_response(message="Logged out successfully", success=True, status=status.HTTP_200_OK)
        except Exception:
            return api_response(message="Invalid or expired refresh token", success=False, status=status.HTTP_400_BAD_REQUEST)
