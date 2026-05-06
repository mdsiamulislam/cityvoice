from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User
from report.models import Report
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from report.models import Report
from django.utils import timezone
from report.models import Assignment
from rest_framework import viewsets
from report.models import ReportImage
from report.serializers import ReportImageSerializer
from report.models import Flag
from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.utils.dateparse import parse_date
from datetime import timedelta
from report.models import Report
import csv
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator
from .models import User
from report.models import Report
from report.serializers import CommentSerializer
from report.models import Notification
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count

from .models import NotificationPreference
from report.models import Report, Vote
from gamification.models import UserBadge
from .serializers import UserProfileSerializer, UpdateProfileSerializer
from .utils import get_civic_rank

# 🔐 REGISTER

class RegisterView(APIView):
    permission_classes = [AllowAny]
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
    

class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

   
        reports_count = Report.objects.filter(reporter=user).count()
        verified_reports = Report.objects.filter(
            reporter=user,
            status='resolved'
        ).count()

        upvotes = Vote.objects.filter(user=user, vote_type='up').count()

        
        badge = UserBadge.objects.filter(user=user).first()
        badge_name = badge.badge.name if badge else None

        
        pref, _ = NotificationPreference.objects.get_or_create(user=user)

      
        rank, percentile = get_civic_rank(user.reputation)

        data = {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "reputation": user.reputation,

            "civic_rank": rank,
            "civic_percentile": percentile,

            "reports_count": reports_count,
            "verified_reports": verified_reports,
            "upvotes": upvotes,

            "badge": badge_name,

            "push_notifications": pref.push_all
        }

        return Response(data)
    

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated"})

        return Response(serializer.errors, status=400)
    

class ToggleNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pref, _ = NotificationPreference.objects.get_or_create(user=request.user)

        pref.push_all = request.data.get('push_notifications', True)
        pref.save()

        return Response({
            "message": "Updated",
            "push_notifications": pref.push_all
        })

# Admin Dashboard Data
class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.all()

        data = {
            "total_reports": reports.count(),
            "pending": reports.filter(status='pending').count(),
            "in_progress": reports.filter(status='in_progress').count(),
            "resolved": reports.filter(status='resolved').count(),

            # zone wise count
            "zone_stats": list(
                reports.values('zone__name')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
        }

        return Response(data)
    

# Action perfom for user in admin dashboard
class AdminUserActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
       

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
        




class NearbyReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'worker':
            return Response({"error": "Only workers allowed"}, status=403)

        assignments = Assignment.objects.filter(
            worker=request.user,
            status__in=['assigned', 'in_progress']
        ).select_related('report')

        data = []
        for a in assignments:
            r = a.report
            data.append({
                "report_id": r.id,
                "title": r.title,
                "description": r.description,
                "address": r.address,
                "priority": r.priority,
                "status": r.status,
                "assignment_status": a.status
            })
        return Response(data)
    


class ResolveReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        note = request.data.get('note')

        try:
            report = Report.objects.get(id=pk)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

        # only assigned worker can resolve
        try:
            assignment = Assignment.objects.get(
                report=report,
                worker=request.user
            )
        except Assignment.DoesNotExist:
            return Response({"error": "Not assigned to you"}, status=403)

        report.status = 'resolved'
        report.resolved_at = timezone.now()
        report.save()

        assignment.status = 'completed'
        assignment.worker_note = note
        assignment.completion_date = timezone.now()
        assignment.save()

        return Response({"message": "Resolved successfully"})
    



class ReportImageViewSet(viewsets.ModelViewSet):
    queryset = ReportImage.objects.all()
    serializer_class = ReportImageSerializer

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == 'worker':
            serializer.save(uploaded_by=user, image_type='after')
        else:
            serializer.save(uploaded_by=user, image_type='before')



class ModerationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        flags = Flag.objects.filter(status='pending')

        data = []
        for f in flags:
            data.append({
                "id": f.id,
                "content_type": f.content_type,
                "content_id": f.content_id,
                "reason": f.reason
            })

        return Response(data)
    

class ModerationActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        action = request.data.get('action')

        try:
            flag = Flag.objects.get(id=pk)
        except Flag.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if action == 'dismiss':
            flag.status = 'resolved'
        elif action == 'review':
            flag.status = 'reviewed'

        flag.save()

        return Response({"message": "Updated"})
    

class DuplicateReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.all()

        duplicates = reports.values('title').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)

        return Response(list(duplicates))
    



class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.order_by('-created_at')[:10]

        data = []
        for r in reports:
            data.append({
                "id": r.id,
                "title": r.title,
                "category": r.category.name,
                "status": r.status,
                "priority": r.priority
            })

        return Response(data)
    
class AssignWorkerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        report_id = request.data.get('report_id')
        worker_id = request.data.get('worker_id')

       
        if not report_id or not worker_id:
            return Response({"error": "report_id and worker_id required"}, status=400)

        try:
            report = Report.objects.get(id=report_id)
        except Report.DoesNotExist:
            return Response({"error": "Report not found"}, status=404)

  
        try:
            worker = User.objects.get(id=worker_id, role='worker')
        except User.DoesNotExist:
            return Response({"error": "Worker not found"}, status=404)


        if Assignment.objects.filter(report=report).exists():
            return Response({"error": "Already assigned"}, status=400)

      
        assignment = Assignment.objects.create(
            report=report,
            worker=worker,
            assigned_by=request.user,
            status='assigned'
        )

        # 🔥 update report status
        report.status = 'in_progress'
        report.save()

        return Response({
            "message": "Assigned successfully",
            "assignment": {
                "report": report.id,
                "worker": worker.username,
                "status": assignment.status
            }
        })
class ReassignWorkerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        report_id = request.data.get('report_id')
        worker_id = request.data.get('worker_id')

        try:
            assignment = Assignment.objects.get(report_id=report_id)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=404)

        try:
            worker = User.objects.get(id=worker_id, role='worker')
        except User.DoesNotExist:
            return Response({"error": "Worker not found"}, status=404)

        assignment.worker = worker
        assignment.status = 'reassigned'
        assignment.save()

        return Response({"message": "Reassigned successfully"})
    
class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

        data = []
        for n in notifications:
            data.append({
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "is_read": n.is_read,
                "created_at": n.created_at
            })

        return Response(data)
    
class MapHeatmapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.values('latitude', 'longitude').annotate(count=Count('id'))

        data = [
            {
                "lat": float(r['latitude']),
                "lng": float(r['longitude']),
                "count": r['count']
            }
            for r in reports
        ]

        return Response(data)
    

class RecentActivityCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = Report.objects.order_by('-created_at')[:50]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="recent_activity.csv"'

        writer = csv.writer(response)
        writer.writerow(['Title', 'Category', 'Status', 'Priority'])

        for r in reports:
            writer.writerow([
                r.title,
                r.category.name,
                r.status,
                r.priority
            ])

        return response

#Analytics Viewwwwwwwwwwwwwwwwwwwwwwwwwwwwwww


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')

        qs = Report.objects.all()

        if start and end:
            qs = qs.filter(created_at__date__range=[parse_date(start), parse_date(end)])

        total = qs.count()
        resolved = qs.filter(status='resolved').count()
        resolution_rate = round((resolved / total * 100), 2) if total else 0

      
        weekly = []
        if start and end:
            s = parse_date(start)
            e = parse_date(end)
            span = (e - s).days + 1
            bucket = max(1, span // 4)

            for i in range(4):
                b_start = s + timedelta(days=i * bucket)
                b_end = min(e, b_start + timedelta(days=bucket - 1))
                count = qs.filter(created_at__date__range=[b_start, b_end]).count()
                weekly.append({
                    "label": f"{b_start} → {b_end}",
                    "count": count
                })
        else:
            weekly = [{"label": f"week_{i+1}", "count": 0} for i in range(4)]

     
        category = list(
            qs.values('category__name')
              .annotate(count=Count('id'))
              .order_by('-count')
        )

   
        duration_expr = ExpressionWrapper(
            F('resolved_at') - F('created_at'),
            output_field=DurationField()
        )

        avg_resp = qs.filter(resolved_at__isnull=False).annotate(
            duration=duration_expr
        ).aggregate(avg=Avg('duration'))['avg']

      
        avg_hours = round(avg_resp.total_seconds() / 3600, 2) if avg_resp else 0

    
        wards = qs.values('zone__name').annotate(
            active_issues=Count('id', filter=Q(status__in=['pending', 'in_progress'])),
            resolved=Count('id', filter=Q(status='resolved')),
            total=Count('id')
        )

        ward_data = []
        for w in wards:
            total_w = w['total'] or 1
            satisfaction = round((w['resolved'] / total_w) * 100, 2)

           
            if satisfaction > 70:
                trend = "up"
            elif satisfaction < 40:
                trend = "down"
            else:
                trend = "flat"

            ward_data.append({
                "zone": w['zone__name'],
                "active_issues": w['active_issues'],
                "avg_response_hours": avg_hours,
                "satisfaction": satisfaction,
                "trend": trend
            })

        return Response({
            "resolution_rate": resolution_rate,
            "weekly": weekly,
            "category": category,
            "avg_response_hours": avg_hours,
            "ward_performance": ward_data
        })






class AnalyticsCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Report.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics.csv"'

        writer = csv.writer(response)
        writer.writerow(['Zone', 'Category', 'Status', 'Created'])

        for r in qs:
            writer.writerow([
                r.zone.name if r.zone else '',
                r.category.name if r.category else '',
                r.status,
                r.created_at
            ])

        return response
    



class AnalyticsPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="analytics.pdf"'

        doc = SimpleDocTemplate(response)
        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph("CityVoice Analytics Report", styles['Title']))
        elements.append(Spacer(1, 12))

        reports = Report.objects.all()[:20]

        for r in reports:
            text = f"{r.title} | {r.status} | {r.zone.name if r.zone else ''}"
            elements.append(Paragraph(text, styles['Normal']))
            elements.append(Spacer(1, 8))

        doc.build(elements)
        return response
    




#for user directory

class UserDirectoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 🔎 params
        role = request.GET.get('role')              
        search = request.GET.get('search')         
        ordering = request.GET.get('ordering')      
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        users = User.objects.all()

        # 🔹 filter by role
        if role:
            users = users.filter(role=role)

        # 🔹 search
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )

        # 🔹 annotate report count
        users = users.annotate(report_count=Count('report'))

        # 🔹 ordering
        if ordering == 'reports':
            users = users.order_by('-report_count')
        elif ordering == 'reputation':
            users = users.order_by('-reputation')
        else:
            users = users.order_by('-id')

        # 🔹 pagination
        paginator = Paginator(users, page_size)
        page_obj = paginator.get_page(page)

        user_list = []
        for u in page_obj:
            status = "flagged" if u.reputation < 100 else "active"

            user_list.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "civic_score": u.reputation,
                "reports": u.report_count,
                "status": status
            })

        # 🔥 metrics
        total_residents = User.objects.filter(role='citizen').count()
        field_workers = User.objects.filter(role='worker').count()
        avg_score = User.objects.aggregate(avg=Avg('reputation'))['avg'] or 0
        flagged_accounts = User.objects.filter(reputation__lt=100).count()

        return Response({
            "metrics": {
                "total_residents": total_residents,
                "field_workers": field_workers,
                "avg_civic_score": round(avg_score, 2),
                "flagged_accounts": flagged_accounts
            },
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count
            },
            "users": user_list
        })
    



class UserCSVExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="users.csv"'

        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Role', 'Score'])

        for u in users:
            writer.writerow([
                u.username,
                u.email,
                u.role,
                u.reputation
            ])

        return response
    



class AdminReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            report = Report.objects.select_related(
                'category', 'zone', 'reporter'
            ).prefetch_related('images', 'comments').get(id=pk)
        except Report.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

      
        assignment = Assignment.objects.filter(report=report).first()

        # 🔥 timeline FIXED
        timeline = {
            "pending": report.created_at,
            "assigned": assignment.created_at if assignment else None,
            "in_progress": assignment.updated_at if assignment else None,
            "resolved": report.resolved_at
        }


        votes = report.upvote_count or 0
        comments_count = report.comment_count or 0

        impact_score = round(min((votes * 0.5 + comments_count * 0.3), 10), 1)

        if impact_score >= 8:
            impact_label = "critical"
        elif impact_score >= 5:
            impact_label = "medium"
        else:
            impact_label = "low"

      
        comments_qs = report.comments.filter(deleted_at__isnull=True).order_by('-created_at')
        comments_data = CommentSerializer(comments_qs, many=True).data

      
        image_url = report.images.first().url if report.images.exists() else None

  
        reporter_name = "Anonymous" if report.is_anonymous else (
            report.reporter.username if report.reporter else "Unknown"
        )

        # 🔥 response
        data = {
            "id": report.id,
            "title": report.title,
            "description": report.description,
            "status": report.status,

            "category": report.category.name if report.category else None,
            "reporter": reporter_name,
            "created_at": report.created_at,
            "zone": report.zone.name if report.zone else None,

            "image": image_url,

            "timeline": timeline,

            "impact": {
                "score": impact_score,
                "label": impact_label
            },

            "comments": comments_data,

            "location": {
                "lat": float(report.latitude) if report.latitude else None,
                "lng": float(report.longitude) if report.longitude else None
            }
        }

        return Response(data)