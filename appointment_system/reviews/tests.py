from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from services.models import Service
from .models import Review

User = get_user_model()


class ReviewAPITest(TestCase):
    """评价系统接口测试"""

    def setUp(self):
        self.client = APIClient()
        # 创建用户
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.provider = User.objects.create_user(username='provider', password='test123', role='provider')
        # 创建服务
        self.service = Service.objects.create(
            provider=self.provider,
            name='测试服务',
            description='测试描述',
            category='医疗',
            price=100,
            duration=60,
            address='测试地址',
        )
        # 获取JWT token
        response = self.client.post('/api/auth/login', {
            'username': 'testuser',
            'password': 'test123'
        })
        self.token = response.data.get('access', '')

    def test_create_review_without_auth(self):
        """未登录用户不能创建评价"""
        response = self.client.post('/api/reviews/', {
            'service': self.service.id,
            'rating': 5,
            'content': '非常好'
        })
        self.assertEqual(response.status_code, 401)

    def test_create_review_success(self):
        """正常创建评价"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post('/api/reviews/', {
            'service': self.service.id,
            'rating': 5,
            'content': '非常好，很专业！'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['code'], 200)

        # 验证数据库中确实有记录
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.service.id, self.service.id)

        # 验证服务评分已更新
        self.service.refresh_from_db()
        self.assertEqual(self.service.rating, 5.0)
        self.assertEqual(self.service.review_count, 1)

    def test_create_review_invalid_rating(self):
        """评分超出范围应该失败"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post('/api/reviews/', {
            'service': self.service.id,
            'rating': 6,
            'content': '评分测试'
        })
        self.assertEqual(response.status_code, 400)

    def test_get_service_reviews(self):
        """查看服务的评价列表"""
        # 先创建几条评价
        Review.objects.create(user=self.user, service=self.service, rating=4, content='不错')
        Review.objects.create(user=self.provider, service=self.service, rating=5, content='很好')

        response = self.client.get(f'/api/reviews/service/{self.service.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.data["data"]
        self.assertEqual(len(data["results"] if isinstance(data, dict) and "results" in data else data), 2)

    def test_multiple_reviews_update_rating(self):
        """多次评价后评分取平均值"""
        Review.objects.create(user=self.user, service=self.service, rating=4, content='还行')
        Review.objects.create(user=self.provider, service=self.service, rating=2, content='一般')

        # 再通过API创建一条
        other_user = User.objects.create_user(username='other', password='test123')
        response = self.client.post('/api/auth/login', {
            'username': 'other',
            'password': 'test123'
        })
        other_token = response.data.get('access', '')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token}')
        self.client.post('/api/reviews/', {
            'service': self.service.id,
            'rating': 5,
            'content': '非常好'
        })

        self.service.refresh_from_db()
        # (4 + 2 + 5) / 3 = 3.67 ≈ 3.7
        self.assertAlmostEqual(self.service.rating, 3.7, delta=0.1)
        self.assertEqual(self.service.review_count, 3)
