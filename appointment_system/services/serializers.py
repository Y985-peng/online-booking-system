from rest_framework import serializers
from .models import Service, ServiceCategory
from django.contrib.auth import get_user_model

User = get_user_model()

class ServiceSerializer(serializers.ModelSerializer):
    """服务数据序列化器 - 把模型数据转换成JSON"""
    provider_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'provider', 'provider_name', 'name', 'description',
            'category', 'price', 'duration', 'address', 'city',
            'is_active', 'views', 'rating', 'review_count',
            'created_at', 'image_url', 'work_start', 'work_end'
        ]
        read_only_fields = ['provider', 'views', 'rating', 'review_count']

    def get_provider_name(self, obj):
        return obj.provider.username if obj.provider else None


class CategorySerializer(serializers.ModelSerializer):
    """服务分类序列化器"""
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name']
