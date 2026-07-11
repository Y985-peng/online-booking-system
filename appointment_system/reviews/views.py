from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from .models import Review
from services.models import Service
from .serializers import ReviewSerializer, CreateReviewSerializer


class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class CreateReviewView(generics.CreateAPIView):
    """创建评价"""
    serializer_class = CreateReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        review = serializer.save(user=self.request.user)
        # 更新服务的平均评分和评价数量
        self._update_service_rating(review.service)

    def _update_service_rating(self, service):
        """更新服务的平均评分和评价数量"""
        result = Review.objects.filter(service=service).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        service.rating = round(result['avg_rating'] or 0, 1)
        service.review_count = result['count'] or 0
        service.save(update_fields=['rating', 'review_count'])

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '评价提交成功',
            'data': response.data
        }, status=status.HTTP_201_CREATED)


class ServiceReviewsView(generics.ListAPIView):
    """查看某个服务的所有评价"""
    serializer_class = ReviewSerializer
    pagination_class = ReviewPagination

    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        return Review.objects.filter(service_id=service_id)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '获取评价列表成功',
            'data': response.data
        })
