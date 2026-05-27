from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class MeView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(UserSerializer(request.user).data)
