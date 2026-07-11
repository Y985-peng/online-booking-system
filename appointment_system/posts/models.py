from django.db import models
from django.conf import settings
from services.models import Service


class Post(models.Model):
    """帖子"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(verbose_name='内容')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联服务')
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True, verbose_name="是否审核通过")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']


class PostLike(models.Model):
    """帖子点赞"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_likes'
        unique_together = ['user', 'post']


class PostFavorite(models.Model):
    """帖子收藏"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_favorites'
        unique_together = ['user', 'post']


class PostComment(models.Model):
    """帖子评论"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_comments'
        ordering = ['created_at']


class Follow(models.Model):
    """关注"""
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'follows'
        unique_together = ['follower', 'following']

class Notification(models.Model):
    """通知（点赞、评论、收藏）"""
    TYPE_CHOICES = [
        ('like', '点赞'),
        ('comment', '评论'),
        ('favorite', '收藏'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField(blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
