from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Zone, Category, Report, Comment, Vote, Follower
from .serializers import ZoneSerializer, CategorySerializer, ReportSerializer, CommentSerializer, VoteSerializer, FollowerSerializer


from rest_framework import response
from rest_framework import status
from rest_framework.views import APIView
from django.db import models


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer



# API Endpoints: Base on Admin Dashboard
class AdminReportView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        reports = Report.objects.all()

        total_reports = reports.count()
        pending_reports = reports.filter(status='pending').count()
        in_progress_reports = reports.filter(status='in_progress').count()
        resolved_reports = reports.filter(status='resolved').count()

        # Zone-wise report counts
        zone_report_counts = reports.values('zone__name').annotate(count=models.Count('id')).order_by('-count')

        dashboard_data = {
            'total_reports': total_reports,
            'pending_reports': pending_reports,
            'in_progress_reports': in_progress_reports,
            'resolved_reports': resolved_reports,
            'zone_report_counts': list(zone_report_counts)
        }

        return response.Response(dashboard_data, status=status.HTTP_200_OK)

    