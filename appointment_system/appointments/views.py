from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Appointment
from services.models import Service
from .serializers import AppointmentSerializer, CreateAppointmentSerializer


# ========== 已有的分页器（可以复用） ==========
class AppointmentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# ========== 已有的创建预约视图（不用动） ==========
import traceback

class CreateAppointmentView(generics.CreateAPIView):
    serializer_class = CreateAppointmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        service_id = self.request.data.get('service')
        service = get_object_or_404(Service, id=service_id, is_active=True)
        serializer.save(
            user=self.request.user,
            status='pending'
        )
    
    def create(self, request, *args, **kwargs):
        # 检查工作时段
        service_id = request.data.get('service')
        if service_id:
            from services.models import Service
            svc = get_object_or_404(Service, id=service_id)
            if svc.work_start and svc.work_end:
                time_str = request.data.get('appointment_time', '')
                if time_str:
                    try:
                        h, m = map(int, time_str.split(':'))
                        start_mins = h * 60 + m
                        end_mins = start_mins + svc.duration
                        ws_mins = svc.work_start.hour * 60 + svc.work_start.minute
                        we_mins = svc.work_end.hour * 60 + svc.work_end.minute
                        ws_display = f'{svc.work_start.hour:02d}:{svc.work_start.minute:02d}'
                        we_display = f'{svc.work_end.hour:02d}:{svc.work_end.minute:02d}'
                        if start_mins < ws_mins:
                            return Response({
                                'code': 400,
                                'message': f'⚠️ 当前非工作时段，工作时段为 {ws_display} - {we_display}'
                            }, status=400)
                        if end_mins > we_mins:
                            return Response({
                                'code': 400,
                                'message': f'⚠️ 预约时间超出工作时段（服务时长{svc.duration}分钟），最晚可预约 {we_display}'
                            }, status=400)
                    except (ValueError, TypeError):
                        pass
                # 检查时段是否已被预约
                from .models import Appointment
                from datetime import time
                date_str = request.data.get('appointment_date')
                if date_str:
                    from datetime import datetime as dt
                    try:
                        apt_date = dt.strptime(date_str, '%Y-%m-%d').date()
                    except:
                        try:
                            apt_date = dt.strptime(date_str, '%Y-%m-%dT%H:%M:%S').date()
                        except:
                            apt_date = None
                    if apt_date:
                        def add_min(t, mins):
                            total = t.hour * 60 + t.minute + mins
                            return time(total // 60 % 24, total % 60)
                        new_h, new_m = map(int, time_str.split(':'))
                        new_start = time(new_h, new_m)
                        new_end = add_min(new_start, svc.duration)
                        existing = Appointment.objects.filter(
                            service=svc, appointment_date=apt_date
                        ).exclude(status='cancelled')
                        for e in existing:
                            es = e.appointment_time
                            ee = add_min(es, svc.duration)
                            if es < new_end and ee > new_start:
                                e_start = f'{es.hour:02d}:{es.minute:02d}'
                                e_end = f'{ee.hour:02d}:{ee.minute:02d}'
                                return Response({
                                    'code': 400,
                                    'message': f'⚠️ {e_start}-{e_end} 已被预约，请选择其他时间'
                                }, status=400)
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                'code': 200,
                'message': '预约成功！等待服务提供者确认',
                'data': response.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            import sys
            print('预约失败:', str(e), file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            return Response({
                'code': 500,
                'message': '预约失败: ' + str(e),
                'error_type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ========== 已有的取消预约视图（不用动） ==========
class CancelAppointmentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        appointment_id = kwargs.get('id')
        appointment = get_object_or_404(
            Appointment, 
            id=appointment_id, 
            user=request.user
        )
        
        if appointment.status == 'cancelled':
            return Response({
                'code': 400,
                'message': '该预约已被取消，无需重复操作'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if appointment.status == 'completed':
            return Response({
                'code': 400,
                'message': '该预约已完成，无法取消'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = 'cancelled'
        appointment.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'code': 200,
            'message': '预约已取消成功',
            'data': {
                'id': appointment.id,
                'service_name': appointment.service.name,
                'appointment_date': appointment.appointment_date,
                'appointment_time': appointment.appointment_time,
                'status': appointment.status
            }
        }, status=status.HTTP_200_OK)


# ========== 🆕 新增：我的预约列表视图 ==========
class MyAppointmentsView(generics.ListAPIView):
    """
    我的预约列表接口
    GET /api/appointments/my/
    需要登录（带JWT Token）
    
    支持参数：
        - status: 状态筛选（pending/confirmed/completed/cancelled）
        - page: 页码
        - page_size: 每页数量
    """
    serializer_class = AppointmentSerializer
    pagination_class = AppointmentPagination
    permission_classes = [IsAuthenticated]  # ← 必须登录
    
    def get_queryset(self):
        """
        返回当前用户的所有预约
        """
        # 1. 只查询当前用户的预约
        queryset = Appointment.objects.filter(user=self.request.user)
        
        # 2. 状态筛选
        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            # 验证状态是否合法
            valid_statuses = ['pending', 'paid', 'confirmed', 'completed', 'cancelled']
            if status_filter in valid_statuses:
                queryset = queryset.filter(status=status_filter)
        
        # 3. 按创建时间倒序排列（最新的在前）
        queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        重写list方法，自定义返回格式
        """
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '获取预约列表成功',
            'data': response.data
        })

class ConfirmAppointmentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        appointment_id = kwargs.get('id')
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # 只有服务提供者才能确认
        if appointment.service.provider != request.user:
            return Response({
                'code': 403,
                'message': '只有服务提供者才能确认预约'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if appointment.status != 'paid':
            return Response({
                'code': 400,
                'message': '该预约尚未支付，无法确认'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = 'confirmed'
        appointment.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'code': 200,
            'message': '预约已确认',
            'data': {
                'id': appointment.id,
                'service_name': appointment.service.name,
                'appointment_date': appointment.appointment_date,
                'appointment_time': appointment.appointment_time,
                'status': appointment.status
            }
        }, status=status.HTTP_200_OK)


class PayAppointmentView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        appointment_id = kwargs.get('id')
        appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
        
        if appointment.status != 'pending':
            return Response({
                'code': 400,
                'message': '该预约状态不允许支付'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        appointment.status = 'paid'
        appointment.save(update_fields=['status', 'updated_at'])
        
        return Response({
            'code': 200,
            'message': '支付成功',
            'data': {
                'id': appointment.id,
                'service_name': appointment.service.name,
                'appointment_date': str(appointment.appointment_date),
                'appointment_time': str(appointment.appointment_time),
                'amount': float(appointment.service.price),
                'status': appointment.status
            }
        }, status=status.HTTP_200_OK)
class ProviderAppointmentsView(generics.ListAPIView):
    """
    服务提供者查看收到的预约列表
    GET /api/appointments/provider/
    需要登录
    """
    serializer_class = AppointmentSerializer
    pagination_class = AppointmentPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        返回当前服务提供者的服务收到的所有预约
        （排除待支付的订单，只显示已支付/已确认/已完成/已取消）
        """
        queryset = Appointment.objects.filter(
            service__provider=self.request.user
        ).order_by('-created_at')

        status_filter = self.request.query_params.get('status', '')
        if status_filter:
            valid_statuses = ['pending', 'paid', 'confirmed', 'completed', 'cancelled']
            if status_filter in valid_statuses:
                queryset = queryset.filter(status=status_filter)

        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '获取服务方预约列表成功',
            'data': response.data
        })
