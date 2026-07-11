from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """评价数据序列化器"""
    username = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'username', 'service', 'service_name',
            'appointment', 'rating', 'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_username(self, obj):
        return obj.user.username if obj.user else None

    def get_service_name(self, obj):
        return obj.service.name if obj.service else None


class CreateReviewSerializer(serializers.ModelSerializer):
    """创建评价专用序列化器"""

    class Meta:
        model = Review
        fields = ['service', 'appointment', 'rating', 'content']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("评分必须在1-5之间")
        return value
