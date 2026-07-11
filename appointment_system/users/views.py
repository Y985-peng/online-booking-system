from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import RegisterSerializer  

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 200,
                'message': '注册成功',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '注册失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from rest_framework.permissions import IsAuthenticated

class UserProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'code': 200,
            'message': '获取用户信息成功',
            'data': {
                'username': user.username,
                'nickname': user.nickname,
                'avatar': user.avatar,
                'role': user.role,
                'phone': user.phone,
            }
        })

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class UpdateProfileView(generics.GenericAPIView):
    """修改个人资料 (support base64)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        nickname = request.data.get('nickname')
        avatar = request.data.get('avatar')
        phone = request.data.get('phone')

        # Store base64 avatar data URL directly (no file system write)
        # avatar is already the base64 data URL from the frontend
        if avatar and not avatar.startswith('data:image') and not avatar.startswith('http'):
            return Response({'code': 400, 'message': '头像格式无效'}, status=400)

        if nickname is not None:
            user.nickname = nickname
        if avatar is not None:
            user.avatar = avatar
        if phone is not None:
            user.phone = phone
        user.save(update_fields=['nickname', 'avatar', 'phone'])

        # Refresh user info
        user.refresh_from_db()
        return Response({
            'code': 200,
            'message': '已更新',
            'data': {
                'username': user.username,
                'nickname': user.nickname,
                'phone': user.phone,
                'role': user.role,
            }
        })




from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions as rest_permissions

class IsAdminPermission(rest_permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class AdminUserListView(generics.GenericAPIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        from django.contrib.auth import get_user_model
        from appointments.models import Appointment
        from services.models import Service
        from reviews.models import Review
        User = get_user_model()
        queryset = User.objects.all().order_by('-date_joined')
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(username__icontains=search)
        data = []
        for u in queryset:
            data.append({
                'id': u.id,
                'username': u.username,
                'role': u.role,
                'phone': u.phone,
                'email': u.email,
                'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M'),
                'stats': {
                    'appointments': Appointment.objects.filter(user=u).count(),
                    'services': Service.objects.filter(provider=u).count(),
                    'reviews': Review.objects.filter(user=u).count(),
                }
            })
        return Response({
            'code': 200,
            'data': {'count': queryset.count(), 'results': data}
        })


class AdminStatsView(generics.GenericAPIView):
    permission_classes = [IsAdminPermission]

    def get(self, request):
        from django.contrib.auth import get_user_model
        from appointments.models import Appointment
        from services.models import Service
        from reviews.models import Review
        User = get_user_model()
        return Response({
            'code': 200,
            'data': {
                'total_users': User.objects.count(),
                'total_providers': User.objects.filter(role='provider').count(),
                'total_admins': User.objects.filter(role='admin').count(),
                'total_services': Service.objects.count(),
                'total_appointments': Appointment.objects.count(),
                'total_reviews': Review.objects.count(),
            }
        })


class ChangePasswordView(generics.GenericAPIView):
    """修改密码"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not old_password or not new_password:
            return Response({'code': 400, 'message': '请填写旧密码和新密码'}, status=400)
        if len(new_password) < 6:
            return Response({'code': 400, 'message': '新密码至少6位'}, status=400)
        if not request.user.check_password(old_password):
            return Response({'code': 400, 'message': '旧密码错误'}, status=400)

        request.user.set_password(new_password)
        request.user.save()
        return Response({'code': 200, 'message': '密码修改成功'})


class UserSearchView(generics.GenericAPIView):
    """搜索用户（用于转发）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response({'code': 200, 'data': []})
        users = User.objects.filter(username__icontains=q).exclude(id=request.user.id)[:10]
        data = [{'id': u.id, 'username': u.username, 'avatar': u.avatar} for u in users]
        return Response({'code': 200, 'data': data})
