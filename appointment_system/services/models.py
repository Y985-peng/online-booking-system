from django.db import models
from django.conf import settings

class Service(models.Model):
    """
    服务模型 - 对应数据库中的服务表
    """
    # 服务提供者（关联到用户表，一个用户可以提供多个服务）
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
        verbose_name='服务提供者'
    )
    
    # 服务基本信息
    name = models.CharField(max_length=100, verbose_name='服务名称')
    description = models.TextField(verbose_name='服务描述')
    category = models.CharField(max_length=50, verbose_name='服务分类')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    duration = models.IntegerField(help_text='单位：分钟', verbose_name='服务时长')
    
    # 地址信息
    address = models.CharField(max_length=200, verbose_name='服务地址')
    city = models.CharField(max_length=50, default='武汉', verbose_name='城市')
    
    # 状态和统计
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    views = models.IntegerField(default=0, verbose_name='浏览次数')
    rating = models.FloatField(default=0.0, verbose_name='评分')
    review_count = models.IntegerField(default=0, verbose_name='评价数量')
    image_url = models.URLField(blank=True, null=True, verbose_name='服务图片')
    work_start = models.TimeField(null=True, blank=True, verbose_name="345267245344275234345274200345247213346227266351227264")
    work_end = models.TimeField(null=True, blank=True, verbose_name="345267245344275234347273223346235237346227266351227264")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'services'  # 指定数据库表名
        ordering = ['-created_at']  # 默认按创建时间倒序排列
        verbose_name = '服务'
        verbose_name_plural = '服务'

    def __str__(self):
        return f"{self.name} - {self.provider.username}"

class TimeSlot(models.Model):
    """
    服务提供者的可用时间段
    """
    DAY_CHOICES = (
        ('monday', '周一'),
        ('tuesday', '周二'),
        ('wednesday', '周三'),
        ('thursday', '周四'),
        ('friday', '周五'),
        ('saturday', '周六'),
        ('sunday', '周日'),
    )

    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='服务提供者'
    )
    day_of_week = models.CharField(max_length=20, choices=DAY_CHOICES, verbose_name='星期')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    is_available = models.BooleanField(default=True, verbose_name='是否可用')

    class Meta:
        db_table = 'time_slots'
        ordering = ['day_of_week', 'start_time']
        verbose_name = '可用时段'
        verbose_name_plural = '可用时段'
        unique_together = ['provider', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class ServiceCategory(models.Model):
    """服务分类（管理员可管理）"""
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'service_categories'
        ordering = ['name']

    def __str__(self):
        return self.name
