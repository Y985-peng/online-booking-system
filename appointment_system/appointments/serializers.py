from rest_framework import serializers
from .models import Appointment
from services.models import Service
from services.serializers import ServiceSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    """预约数据序列化器"""
    
    # 显示关联对象的详细信息
    user_username = serializers.SerializerMethodField()
    service_detail = ServiceSerializer(source='service', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'user', 'user_username', 
            'service', 'service_detail',
            'appointment_date', 'appointment_time',
            'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']

    def get_user_username(self, obj):
        return obj.user.username if obj.user else None


class CreateAppointmentSerializer(serializers.ModelSerializer):
    """
    创建预约专用序列化器
    用户只需要传: service_id, appointment_date, appointment_time, notes(可选)
    """
    
    class Meta:
        model = Appointment
        fields = ['id', 'service', 'appointment_date', 'appointment_time', 'notes']
    
    def validate(self, data):
        # 检查该时段是否已被预约
        existing = Appointment.objects.filter(
            service=data['service'],
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time']
        ).exclude(status='cancelled')
        if existing.exists():
            raise serializers.ValidationError('该时段已被预约，请选择其他时间')
        return data