from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly,AllowAny,IsAuthenticated
from .models import Zone, Category, Report, Comment, Vote, Follower
from .serializers import ZoneSerializer, CategorySerializer, ReportSerializer, CommentSerializer, VoteSerializer, FollowerSerializer
from .models import ReportUpdate,Flag
from rest_framework.response import Response
from rest_framework import response
from rest_framework import status
from rest_framework.views import APIView
from django.db import models
from django.utils import timezone
from report.models import Assignment
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

    def get_queryset(self):
        user = self.request.user
        my_reports = self.request.query_params.get('my_reports')

    
        if my_reports == 'true' and user.is_authenticated:
            return Report.objects.filter(reporter=user)

    
        return Report.objects.all().order_by('-created_at')
    # def get_queryset(self):
    #     queryset = Report.objects.all()

    #     search = self.request.query_params.get('search')
    #     status = self.request.query_params.get('status')
    #     category = self.request.query_params.get('category')

    #     if search:
    #         queryset = queryset.filter(title__icontains=search)

    #     if status:
    #         queryset = queryset.filter(status=status)

    #     if category:
    #         queryset = queryset.filter(category__id=category)

    #     return queryset.order_by('-created_at')
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)



class AllReportView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reports = Report.objects.all().order_by('-created_at')

        data = [
            {
                "id": r.id,
                "title": r.title,
                "status": r.status,
                "category": r.category.name,
                "zone": r.zone.name if r.zone else None
            }
            for r in reports
        ]

        return Response(data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.filter(
            deleted_at__isnull=True
        )

        report_id = self.request.query_params.get('report')

        if report_id:
            queryset = queryset.filter(report_id=report_id)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):

        comment = self.get_object()

        # ownership check
        if comment.user != request.user:
            return Response({
                "error": "Permission denied"
            }, status=403)

        comment.deleted_at = timezone.now()

        comment.save()

        return Response({
            "message": "Comment deleted"
        })

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Vote.objects.all()

    def create(self, request, *args, **kwargs):

        report_id = request.data.get('report')
        vote_type = request.data.get('vote_type')

        try:
            report = Report.objects.get(id=report_id)

        except Report.DoesNotExist:
            return Response({
                "error": "Report not found"
            }, status=404)

        vote = Vote.objects.filter(
            user=request.user,
            report=report
        ).first()

        # remove same vote
        if vote and vote.vote_type == vote_type:

            if vote.vote_type == 'up':
                report.upvote_count -= 1

            else:
                report.downvote_count -= 1

            report.save()

            vote.delete()

            return Response({
                "message": "Vote removed"
            })

        # update existing vote
        if vote:

            # old remove
            if vote.vote_type == 'up':
                report.upvote_count -= 1

            else:
                report.downvote_count -= 1

            # new add
            if vote_type == 'up':
                report.upvote_count += 1

            else:
                report.downvote_count += 1

            vote.vote_type = vote_type
            vote.save()

            report.save()

            return Response({
                "message": "Vote updated"
            })

        # create new vote
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save(user=request.user)

        if vote_type == 'up':
            report.upvote_count += 1

        else:
            report.downvote_count += 1

        report.save()

        return Response(serializer.data)




class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



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



class ReportTimelineView(APIView):
    def get(self, request, report_id):
        updates = ReportUpdate.objects.filter(report_id=report_id).order_by('created_at')

        data = [
            {
                "status": u.new_status,
                "time": u.created_at,
                "note": u.body
            }
            for u in updates
        ]

        return Response(data)
    


class FlagReportView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        Flag.objects.create(
            reporter=request.user,
            content_type='report',
            content_id=request.data.get('report'),
            reason=request.data.get('reason')
        )
        return Response({"message": "Report flagged"})
    


class CancelReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            report = Report.objects.get(id=pk, reporter=request.user)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        if report.status in ['resolved']:
            return Response({"error": "Cannot cancel resolved report"}, status=400)

        report.status = 'cancelled'
        report.save()

        return Response({"message": "Report cancelled"})

