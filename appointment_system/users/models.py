from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    自定义用户模型
    """
    ROLE_CHOICES = (
        ('user', '普通用户'),
        ('provider', '服务提供者'),
        ('admin', '管理员'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone = models.CharField(max_length=11, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
