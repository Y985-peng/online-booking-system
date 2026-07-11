from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from services.models import Service, TimeSlot

User = get_user_model()


class ServiceAPITest(TestCase):
    """服务发布和管理接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.provider = User.objects.create_user(username='provider', password='test123', role='provider')
        self.user = User.objects.create_user(username='testuser', password='test123')
        # 登录
        response = self.client.post('/api/auth/login', {
            'username': 'provider',
            'password': 'test123'
        })
        self.token = response.data.get('access', '')

    def test_publish_service_without_auth(self):
        """未登录不能发布服务"""
        response = self.client.post('/api/services/publish/', {
            'name': '新服务',
            'category': '美容',
            'price': 200,
            'duration': 60,
            'address': '武汉',
            'description': '描述'
        })
        self.assertEqual(response.status_code, 401)

    def test_publish_service_success(self):
        """服务提供者成功发布服务"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post('/api/services/publish/', {
            'name': '专业美容护理',
            'category': '美容',
            'price': 200,
            'duration': 60,
            'address': '武汉市洪山区',
            'description': '专业美容护理服务'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.first().provider, self.provider)

    def test_my_services(self):
        """查看自己发布的服务"""
        Service.objects.create(provider=self.provider, name='服务1', category='医疗', price=100, duration=30, address='addr')
        Service.objects.create(provider=self.provider, name='服务2', category='美容', price=200, duration=60, address='addr')
        # 另一个用户的服务
        other = User.objects.create_user(username='other', password='test123')
        Service.objects.create(provider=other, name='服务3', category='健身', price=150, duration=45, address='addr')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get('/api/services/my/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 2)

    def test_delete_service(self):
        """删除自己发布的服务"""
        service = Service.objects.create(provider=self.provider, name='待删除', category='其他', price=50, duration=30, address='addr')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.delete(f'/api/services/{service.id}/manage/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Service.objects.filter(is_active=True).count(), 0)


class TimeSlotAPITest(TestCase):
    """时段设置接口测试"""

    def setUp(self):
        self.client = APIClient()
        self.provider = User.objects.create_user(username='provider2', password='test123', role='provider')
        response = self.client.post('/api/auth/login', {
            'username': 'provider2',
            'password': 'test123'
        })
        self.token = response.data.get('access', '')

    def test_add_time_slot(self):
        """添加可用时段"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.post('/api/services/time-slots/', {
            'day_of_week': 'monday',
            'start_time': '09:00',
            'end_time': '18:00',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TimeSlot.objects.count(), 1)

    def test_get_time_slots(self):
        """获取时段列表"""
        TimeSlot.objects.create(provider=self.provider, day_of_week='monday', start_time='09:00', end_time='12:00')
        TimeSlot.objects.create(provider=self.provider, day_of_week='tuesday', start_time='10:00', end_time='16:00')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        response = self.client.get('/api/services/time-slots/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 2)
