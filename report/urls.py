from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ZoneViewSet , CategoryViewSet, ReportViewSet, CommentViewSet, VoteViewSet, FollowerViewSet, AdminReportView,ReportTimelineView,FlagReportView,AllReportView,CancelReportView
from user.views import ReportImageViewSet
router = DefaultRouter()
router.register('zones', ZoneViewSet)
router.register('categories', CategoryViewSet)
router.register('reports', ReportViewSet)
router.register('comments', CommentViewSet)
router.register('votes', VoteViewSet)
router.register('followers', FollowerViewSet)
router.register('report-images', ReportImageViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/admin/reports/', AdminReportView.as_view(), name='admin-reports'),
    path('api/reports/<int:report_id>/timeline/', ReportTimelineView.as_view()),
    path('api/flag/', FlagReportView.as_view()),
    path('api/all-reports/', AllReportView.as_view()),
    path('api/reports/<int:pk>/cancel/', CancelReportView.as_view())
]