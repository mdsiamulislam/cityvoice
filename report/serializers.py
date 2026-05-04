from rest_framework import serializers
from .models import Zone, Category, Report, Comment, Vote, Follower, ReportImage


# ───────────── BASIC ─────────────

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


# ───────────── REPORT IMAGES ─────────────

class ReportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportImage
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'created_at']


# ───────────── COMMENTS ─────────────

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

    def get_replies(self, obj):
        replies = obj.replies.filter(deleted_at__isnull=True)
        return CommentSerializer(replies, many=True).data


# ───────────── VOTE ─────────────

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        report = data['report']

        if Vote.objects.filter(user=user, report=report).exists():
            raise serializers.ValidationError("Already voted")

        return data


# ───────────── FOLLOWER ─────────────

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        report = data['report']

        if Follower.objects.filter(user=user, report=report).exists():
            raise serializers.ValidationError("Already following")

        return data


# ───────────── REPORT ─────────────

class ReportSerializer(serializers.ModelSerializer):
    images = ReportImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    category_name = serializers.CharField(source='category.name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)

    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = [
            'reporter',
            'priority_score',
            'upvote_count',
            'downvote_count',
            'comment_count',
            'follower_count',
            'view_count',
        ]