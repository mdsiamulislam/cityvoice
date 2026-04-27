
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', views.UserList.as_view(), name='user-list'),
]
