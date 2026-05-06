from rest_framework import serializers
from .models import User
from rest_framework import serializers
from .models import User, NotificationPreference
from report.models import Report, Vote
from gamification.models import UserBadge

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