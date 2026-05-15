from django.urls import path
from .views import (RegisterView, LoginView, ProfileView,AdminDashboardView, AdminUserActionView,ModerationView,ModerationActionView, FCMTokenViewSet,
                    DuplicateReportView,RecentActivityView,
                    AnalyticsView, AnalyticsCSVView, AnalyticsPDFView,UserDirectoryView, 
                    UserCSVExportView,AdminReportDetailView,AssignWorkerView,
                    ReassignWorkerView,NotificationView,MapHeatmapView,RecentActivityCSVView,UserProfileDetailView,UpdateProfileView,ToggleNotificationView,WorkerStatsView)
from .views import NearbyReportView, ResolveReportView
from .views import ReportImageViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('report-images', ReportImageViewSet)
urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('fcm-tokens/', FCMTokenViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('worker/nearby/', NearbyReportView.as_view()),
    path('reports/<int:pk>/resolve/', ResolveReportView.as_view()),
    path('admin/user/dashboard/', AdminDashboardView.as_view()),
    path('admin/user/action/<int:user_id>/', AdminUserActionView.as_view()),
    path('admin/moderation/', ModerationView.as_view()),
    path('admin/moderation/<int:pk>/', ModerationActionView.as_view()),
    path('admin/duplicates/', DuplicateReportView.as_view()),
    path('admin/recent-activity/', RecentActivityView.as_view()),
    path('admin/analytics/', AnalyticsView.as_view()),
    path('admin/analytics/csv/', AnalyticsCSVView.as_view()),
    path('admin/analytics/pdf/', AnalyticsPDFView.as_view()),
    path('admin/users/', UserDirectoryView.as_view()),
    path('admin/users/csv/', UserCSVExportView.as_view()),
    path('admin/reports/<int:pk>/', AdminReportDetailView.as_view()),
    path('admin/assign/', AssignWorkerView.as_view()),
    path('admin/reassign/', ReassignWorkerView.as_view()),
    path('notifications/', NotificationView.as_view()),
    path('admin/map-heat/', MapHeatmapView.as_view()),
    path('admin/recent-activity/csv/', RecentActivityCSVView.as_view()),
    path('profile/detail/', UserProfileDetailView.as_view()),
    path('profile/update/', UpdateProfileView.as_view()),
    path('profile/notifications/', ToggleNotificationView.as_view()),
    path('worker/stats/', WorkerStatsView.as_view()),
]
urlpatterns += router.urls