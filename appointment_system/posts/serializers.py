from rest_framework import serializers
from .models import Post, PostLike, PostFavorite, PostComment, Follow, Notification
from django.contrib.auth import get_user_model

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    service_id = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'username', 'user_role',
            'content', 'service', 'service_name', 'service_id',
            'is_approved', 'like_count', 'comment_count', 'is_liked', 'is_favorited',
            'created_at'
        ]
        read_only_fields = ['user']

    def get_username(self, obj):
        return obj.user.username

    def get_user_role(self, obj):
        return obj.user.role

    def get_service_name(self, obj):
        return obj.service.name if obj.service else None

    def get_service_id(self, obj):
        return obj.service.id if obj.service else None

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return False
        return PostLike.objects.filter(user=user, post=obj).exists()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user or not user.is_authenticated:
            return False
        return PostFavorite.objects.filter(user=user, post=obj).exists()


class PostCommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = ['id', 'user', 'username', 'content', 'created_at']
        read_only_fields = ['user']

    def get_username(self, obj):
        return obj.user.username


class NotificationSerializer(serializers.ModelSerializer):
    from_username = serializers.SerializerMethodField()
    post_content = serializers.SerializerMethodField()
    post_id = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'type', 'from_user', 'from_username', 'post', 'post_id', 'post_content', 'content', 'is_read', 'created_at']

    def get_from_username(self, obj):
        return obj.from_user.username

    def get_post_content(self, obj):
        return obj.post.content[:60] if obj.post else ''

    def get_post_id(self, obj):
        return obj.post.id if obj.post else None
