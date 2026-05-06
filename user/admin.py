from django.contrib import admin
from .models import User, RefreshToken, OTPCode, NotificationPreference


# 👤 Custom User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'role',
        'is_verified', 'phone_verified',
        'reputation', 'is_staff', 'is_active'
    )
    list_filter = ('role', 'is_verified', 'phone_verified', 'is_staff')
    search_fields = ('username', 'email', 'full_name', 'phone')
    ordering = ('-id',)
    readonly_fields = ('deleted_at',)

    fieldsets = (
        ("Basic Info", {
            'fields': ('username', 'full_name', 'email', 'phone', 'photo_url')
        }),
        ("Auth", {
            'fields': ('password', 'is_staff', 'is_superuser', 'is_active')
        }),
        ("Roles & Status", {
            'fields': ('role', 'is_verified', 'phone_verified', 'reputation')
        }),
        ("Notifications", {
            'fields': ('push_enabled', 'email_notif', 'fcm_token')
        }),
        ("Other", {
            'fields': ('google_id', 'deleted_at')
        }),
    )


# 🔐 Refresh Token Admin
@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'device_info', 'expires_at', 'revoked', 'created_at')
    list_filter = ('revoked', 'created_at')
    search_fields = ('user__username', 'device_info')
    ordering = ('-created_at',)


# 🔢 OTP Code Admin
@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'purpose', 'code', 'expires_at', 'used', 'created_at')
    list_filter = ('purpose', 'used')
    search_fields = ('user__username', 'code')
    ordering = ('-created_at',)


# 🔔 Notification Preferences Admin
@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'push_all', 'push_own',
        'push_followed', 'push_nearby',
        'email_weekly', 'email_status', 'updated_at'
    )
    list_filter = ('push_all', 'push_nearby', 'email_weekly')
    search_fields = ('user__username',)