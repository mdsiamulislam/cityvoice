from django.contrib import admin
from .models import (
    Zone, Category, Report, ReportImage, ReportDraft,
    Vote, Follower, Comment, CommentReaction,
    Assignment, ReportUpdate,
    Notification, Flag
)


# 🌍 Zone
@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'created_at')
    search_fields = ('name', 'city')
    ordering = ('-created_at',)


# 📂 Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color_hex', 'sla_hours', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


# 🖼️ Report Images Inline
class ReportImageInline(admin.TabularInline):
    model = ReportImage
    extra = 1


# 📢 Report
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'zone',
        'status', 'priority', 'reporter',
        'created_at'
    )
    list_filter = ('status', 'priority', 'category', 'zone')
    search_fields = ('title', 'description', 'address')
    ordering = ('-created_at',)
    inlines = [ReportImageInline]

    readonly_fields = (
        'upvote_count', 'downvote_count',
        'comment_count', 'follower_count', 'view_count'
    )


# 🖼️ Report Image
@admin.register(ReportImage)
class ReportImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'report', 'url', 'image_type', 'uploaded_by', 'created_at']
    list_filter = ['image_type', 'created_at']
    search_fields = ['report__title']


# 📝 Draft
@admin.register(ReportDraft)
class ReportDraftAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'updated_at')
    search_fields = ('user__username',)


# 👍 Vote
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'report', 'vote_type', 'created_at')
    list_filter = ('vote_type',)
    search_fields = ('user__username', 'report__title')


# ⭐ Follower
@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'report', 'created_at')
    search_fields = ('user__username', 'report__title')


# 💬 Comment
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fk_name = 'report'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'report', 'is_flagged', 'created_at')
    list_filter = ('is_flagged',)
    search_fields = ('user__username', 'body')


# ❤️ Comment Reaction
@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'reaction', 'created_at')
    search_fields = ('user__username',)


# 🛠️ Assignment
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'report', 'worker', 'assigned_by',
        'status', 'due_date', 'created_at'
    )
    list_filter = ('status',)
    search_fields = ('worker__username', 'report__title')


# 🔄 Report Updates (Timeline)
@admin.register(ReportUpdate)
class ReportUpdateAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'author', 'new_status', 'created_at')
    search_fields = ('report__title', 'author__username')


# 🔔 Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'title')


# 🚨 Flag (Moderation)
@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'content_type', 'content_id', 'status', 'created_at')
    list_filter = ('status', 'content_type')
    search_fields = ('reporter__username', 'reason')