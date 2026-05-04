from django.urls import path
from .views import RegisterView, LoginView, ProfileView, AdminDashboardView, AdminUserActionView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),

    path('admin/user/dashboard/', AdminDashboardView.as_view()),
    path('admin/user/action/<int:user_id>/', AdminUserActionView.as_view()),
]