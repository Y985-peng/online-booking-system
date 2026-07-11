from django.db import models
from django.conf import settings
from services.models import Service


class Review(models.Model):
    """
    评价模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='评价用户'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='评价服务'
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name='关联预约'
    )
    rating = models.IntegerField(verbose_name='评分', default=5)
    content = models.TextField(verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        verbose_name = '评价'
        verbose_name_plural = '评价'

    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.rating}星"
