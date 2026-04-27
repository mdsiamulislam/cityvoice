from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('citizen', 'Citizen'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )
    
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    google_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    photo_url = models.URLField(max_length=500, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='citizen')
    is_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    reputation = models.IntegerField(default=0)
    push_enabled = models.BooleanField(default=True)
    email_notif = models.BooleanField(default=True)
    fcm_token = models.CharField(max_length=300, blank=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Overriding standard fields
    first_name = None
    last_name = None
    username = models.CharField(max_length=150, unique=True) 

    def __str__(self):
        return self.full_name or self.username

class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token_hash = models.CharField(max_length=255, unique=True)
    device_info = models.CharField(max_length=300, blank=True, null=True)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class OTPCode(models.Model):
    PURPOSE_CHOICES = (
        ('email_verify', 'Email Verify'),
        ('password_reset', 'Password Reset'),
        ('phone_verify', 'Phone Verify'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    push_all = models.BooleanField(default=True)
    push_own = models.BooleanField(default=True)
    push_followed = models.BooleanField(default=True)
    push_nearby = models.BooleanField(default=False)
    email_weekly = models.BooleanField(default=True)
    email_status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
