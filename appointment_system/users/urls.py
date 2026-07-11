from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CustomTokenObtainPairView, UserProfileView
from .views import UpdateProfileView
from .views import AdminUserListView, AdminStatsView, ChangePasswordView, UserSearchView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh', TokenRefreshView.as_view()),
    path('profile', UserProfileView.as_view(), name='profile'),
    path('profile/update', UpdateProfileView.as_view(), name='profile-update'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),
    path('search/', UserSearchView.as_view(), name='user-search'),
]
