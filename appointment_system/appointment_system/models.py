from django.db import models
from django.conf import settings
from services.models import Service

class Appointment(models.Model):
    """
    预约模型 - 对应数据库中的预约表
    """
    # 预约状态枚举
    STATUS_CHOICES = (
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    
    # 关联：谁预约的、预约了什么服务
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='预约用户'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='预约服务'
    )
    
    # 预约时间
    appointment_date = models.DateField(verbose_name='预约日期')
    appointment_time = models.TimeField(verbose_name='预约时间')
    
    # 预约状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='预约状态'
    )
    
    # 备注
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-created_at']
        verbose_name = '预约'
        verbose_name_plural = '预约'
        # 保证同一个服务同一个时间段不能重复预约
        unique_together = ['service', 'appointment_date', 'appointment_time']

    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.appointment_date} {self.appointment_time}"