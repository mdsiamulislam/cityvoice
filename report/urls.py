from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ZoneViewSet , CategoryViewSet, ReportViewSet, CommentViewSet, VoteViewSet, FollowerViewSet, AdminReportView

router = DefaultRouter()
router.register('zones', ZoneViewSet)
router.register('categories', CategoryViewSet)
router.register('reports', ReportViewSet)
router.register('comments', CommentViewSet)
router.register('votes', VoteViewSet)
router.register('followers', FollowerViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/admin/reports/', AdminReportView.as_view(), name='admin-reports'),
]