from rest_framework import serializers
from .models import User
from rest_framework import serializers
from .models import User, NotificationPreference
from report.models import Report, Vote
from gamification.models import UserBadge
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
            'email',
            'phone',
            'password'
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            full_name=validated_data.get('full_name'),
            email=validated_data['email'],
            phone=validated_data.get('phone'),
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']


    
class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    reputation = serializers.IntegerField()

    civic_rank = serializers.CharField()
    civic_percentile = serializers.CharField()

    reports_count = serializers.IntegerField()
    verified_reports = serializers.IntegerField()
    upvotes = serializers.IntegerField()

    badge = serializers.CharField(allow_null=True)

    push_notifications = serializers.BooleanField()


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone']


    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=10)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class UserPublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'civic_rank', 'reputation', 'photo_url']