from django.db import models
from django.utils import timezone
from django.conf import settings


# ZONES & CATEGORIES

class Zone(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    boundary = models.JSONField(help_text='GeoJSON format or list of lat/lng pairs')  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city})"

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    color_hex = models.CharField(max_length=7, default='#607D8B')
    weight = models.FloatField(default=1.0)
    sla_hours = models.IntegerField(default=72)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# REPORTS (CORE)

class Report(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'), ('pending', 'Pending'), ('under_review', 'Under Review'),
        ('in_progress', 'In Progress'), ('resolved', 'Resolved'), 
        ('rejected', 'Rejected'), ('duplicate', 'Duplicate'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    priority_score = models.FloatField(default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    address = models.CharField(max_length=300, blank=True, null=True)
    
    # Counter Caching
    upvote_count = models.IntegerField(default=0)
    downvote_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    resolved_at = models.DateTimeField(null=True, blank=True)
    estimated_date = models.DateField(null=True, blank=True)
    admin_note = models.TextField(blank=True, null=True)
    duplicate_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class ReportImage(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='images')
    url = models.URLField(max_length=500)
    caption = models.CharField(max_length=200, blank=True, null=True)
    is_before = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ReportDraft(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_json = models.JSONField()
    updated_at = models.DateTimeField(auto_now=True)

# ─────────────────────────────────────────
# VOTES, FOLLOWS & COMMENTS
# ─────────────────────────────────────────

class Vote(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=(('up', 'Up'), ('down', 'Down')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'report')

class Follower(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'report')

class Comment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

class CommentReaction(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10) # like, love, wow
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

# ─────────────────────────────────────────
# ASSIGNMENTS & UPDATES
# ─────────────────────────────────────────

class Assignment(models.Model):
    STATUS_CHOICES = (
        ('assigned', 'Assigned'), ('accepted', 'Accepted'), 
        ('in_progress', 'In Progress'), ('completed', 'Completed'), ('reassigned', 'Reassigned'),
    )
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    worker_note = models.TextField(blank=True, null=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ReportUpdate(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='updates')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    update_type = models.CharField(max_length=20)
    old_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

# ─────────────────────────────────────────
# NOTIFICATIONS & MODERATION
# ─────────────────────────────────────────

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=60)
    title = models.CharField(max_length=150)
    body = models.TextField(blank=True, null=True)
    data_json = models.JSONField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Flag(models.Model):
    CONTENT_CHOICES = (('report', 'Report'), ('comment', 'Comment'))
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=CONTENT_CHOICES)
    content_id = models.IntegerField()
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)