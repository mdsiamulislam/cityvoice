from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User


# 🔐 REGISTER

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User created",
                "user": UserSerializer(user).data
            })

        return Response(serializer.errors, status=400)


# 🔐 LOGIN

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user:
                refresh = RefreshToken.for_user(user)

                return Response({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data
                })

            return Response({"error": "Invalid credentials"}, status=401)

        return Response(serializer.errors, status=400)


# 👤 PROFILE

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
    


# Admin Dashboard Data
class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # if not request.user.is_staff:
        #     return Response({"error": "Unauthorized"}, status=403)

        total_users = User.objects.count()
        staff_users = User.objects.filter(is_staff=True).count()

        all_users = User.objects.all()

        response_data = {
            "total_users": total_users,
            "staff_users": staff_users,
            "users": UserSerializer(all_users, many=True).data
        }

        return Response(response_data)
    

# Action perfom for user in admin dashboard
class AdminUserActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        # if not request.user.is_staff:
        #     return Response({"error": "Unauthorized"}, status=403)

        action = request.data.get('action')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if action == 'promote':
            user.is_staff = True
            user.save()
            return Response({"message": f"{user.username} promoted to staff"})

        elif action == 'demote':
            user.is_staff = False
            user.save()
            return Response({"message": f"{user.username} demoted from staff"})

        elif action == 'delete':
            user.delete()
            return Response({"message": f"{user.username} deleted"})

        else:
            return Response({"error": "Invalid action"}, status=400)