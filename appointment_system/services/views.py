from django.shortcuts import render

# Create your views here.
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Service, ServiceCategory
from .serializers import ServiceSerializer


# ========== 自定义分页器 ==========
class ServicePagination(PageNumberPagination):
    """服务列表分页配置"""
    page_size = 10  # 每页显示10条
    page_size_query_param = 'page_size'
    max_page_size = 50


# ========== 服务列表接口（支持搜索/分类/分页） ==========
class ServiceListView(generics.ListAPIView):
    """
    服务列表查询接口
    GET /api/services/
    支持参数：
        - search: 关键词搜索（服务名称/描述/地址）
        - category: 分类筛选
        - city: 城市筛选
        - min_price: 最低价格
        - max_price: 最高价格
        - ordering: 排序（price, -price, rating, -rating, duration）
    """
    serializer_class = ServiceSerializer
    pagination_class = ServicePagination

    def get_queryset(self):
        """根据请求参数动态构建查询条件"""
        queryset = Service.objects.filter(is_active=True)  # 只显示上架的服务
        
        # 1. 关键词搜索
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |          # 服务名称包含关键词
                Q(description__icontains=search) |   # 服务描述包含关键词
                Q(address__icontains=search)         # 服务地址包含关键词
            )
        
        # 2. 分类筛选
        category = self.request.query_params.get('category', '')
        if category:
            queryset = queryset.filter(category=category)
        
        # 3. 城市筛选
        city = self.request.query_params.get('city', '')
        if city:
            queryset = queryset.filter(city=city)
        
        # 4. 价格区间
        min_price = self.request.query_params.get('min_price', '')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        max_price = self.request.query_params.get('max_price', '')
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # 5. 排序
        ordering = self.request.query_params.get('ordering', '-created_at')
        allowed_orderings = ['price', '-price', 'rating', '-rating', 'duration', '-duration', 'created_at', '-created_at']
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '获取服务列表成功',
            'data': response.data
        })


# ========== 获取所有分类列表 ==========
class CategoryListView(generics.GenericAPIView):
    """获取所有服务分类"""
    def get(self, request):
        cat_objs = ServiceCategory.objects.all()
        cat_names_lower = set(c.name.strip().lower() for c in cat_objs)
        seen = set()
        result = []
        # ServiceCategory 记录
        for c in cat_objs:
            key = c.name.strip().lower()
            if key not in seen:
                seen.add(key)
                result.append({'id': c.id, 'name': c.name.strip()})
        # 现有服务中的分类（去重）
        svc_cats = Service.objects.values_list('category', flat=True).distinct()
        for name in svc_cats:
            clean = name.strip() if name else ''
            key = clean.lower()
            if clean and key not in seen and key not in cat_names_lower:
                seen.add(key)
                result.append({'id': None, 'name': clean})
        data = result
        return Response({'code': 200, 'data': data})


class AdminCategoryCreateView(generics.GenericAPIView):
    """管理员新增分类"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            return Response({'code': 403, 'message': '仅管理员可操作'}, status=403)
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'code': 400, 'message': '分类名不能为空'}, status=400)
        cat, created = ServiceCategory.objects.get_or_create(name=name)
        if not created:
            return Response({'code': 400, 'message': '分类已存在'}, status=400)
        from .serializers import CategorySerializer
        return Response({'code': 201, 'data': CategorySerializer(cat).data}, status=201)


class AdminCategoryDeleteView(generics.GenericAPIView):
    """管理员删除分类"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, cat_id):
        if request.user.role != 'admin':
            return Response({'code': 403, 'message': '仅管理员可操作'}, status=403)
        cat = get_object_or_404(ServiceCategory, id=cat_id)
        cat.delete()
        return Response({'code': 200, 'message': '已删除'})
    

class ServiceDetailView(generics.RetrieveAPIView):
    """
    服务详情接口
    GET /api/services/{id}/
    返回某个服务的完整信息
    同时自动增加浏览次数
    """
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    lookup_field = 'id'  # 根据 URL 中的 id 查找

    def retrieve(self, request, *args, **kwargs):
        # 获取服务对象
        service = self.get_object()
        
        # 浏览次数 +1
        service.views += 1
        service.save(update_fields=['views'])
        
        # 序列化返回
        serializer = self.get_serializer(service)
        return Response({
            'code': 200,
            'message': '获取服务详情成功',
            'data': serializer.data
        })
# ========== 发布服务（需要登录） ==========
from rest_framework.permissions import IsAuthenticated
from rest_framework import status



def _save_service_image(request, image_data):
    import os, uuid, base64
    from django.conf import settings
    try:
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        if ext == 'jpeg': ext = 'jpg'
        filename = f'service_{uuid.uuid4().hex[:8]}.{ext}'
        upload_dir = os.path.join(settings.BASE_DIR, 'media', 'services')
        os.makedirs(upload_dir, exist_ok=True)
        with open(os.path.join(upload_dir, filename), 'wb') as f:
            f.write(base64.b64decode(imgstr))
        return request.build_absolute_uri(f'/media/services/{filename}')
    except:
        return image_data

class CreateServiceView(generics.CreateAPIView):
    """发布新服务"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

    def create(self, request, *args, **kwargs):
        image_url = request.data.get('image_url', '')
        if image_url and image_url.startswith('data:image'):
            url = _save_service_image(request, image_url)
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            data['image_url'] = url
            request._full_data = data
        response = super().create(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '服务发布成功',
            'data': response.data
        }, status=status.HTTP_201_CREATED)


class MyServicesView(generics.ListAPIView):
    """查看我发布的服务"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Service.objects.filter(provider=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '获取我的服务列表成功',
            'data': response.data
        })


class ServiceManageView(generics.RetrieveUpdateDestroyAPIView):
    """更新或删除自己发布的服务"""
    serializer_class = ServiceSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "id"

    def get_queryset(self):
        return Service.objects.filter(provider=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        image_url = request.data.get('image_url', '')
        if image_url and image_url.startswith('data:image'):
            url = _save_service_image(request, image_url)
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            data['image_url'] = url
            request._full_data = data
        response = super().update(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '服务更新成功',
            'data': response.data
        })

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '服务删除成功'
        }, status=status.HTTP_200_OK)


class ProviderDashboardView(generics.GenericAPIView):
    """服务提供者看板数据"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from appointments.models import Appointment
        from reviews.models import Review
        from django.db.models import Sum, Avg, Count
        from django.utils import timezone

        my_services = Service.objects.filter(provider=user)
        total_services = my_services.count()
        service_ids = my_services.values_list('id', flat=True)

        today = timezone.now().date()
        today_appointments = Appointment.objects.filter(
            service_id__in=service_ids,
            appointment_date=today
        ).count()

        month_start = today.replace(day=1)
        month_appointments = Appointment.objects.filter(
            service_id__in=service_ids,
            status='completed',
            appointment_date__gte=month_start,
            appointment_date__lte=today
        )
        total_income = sum(float(apt.service.price) for apt in month_appointments)

        reviews = Review.objects.filter(service_id__in=service_ids)
        total_reviews = reviews.count()
        good_reviews = reviews.filter(rating__gte=4).count()
        good_rate = round(good_reviews / total_reviews * 100, 1) if total_reviews > 0 else 100

        recent_appointments = Appointment.objects.filter(
            service_id__in=service_ids
        ).select_related('user', 'service').order_by('-appointment_date', '-appointment_time')[:10]

        recent_list = []
        for apt in recent_appointments:
            recent_list.append({
                'id': apt.id,
                'username': apt.user.username,
                'service_name': apt.service.name,
                'appointment_date': str(apt.appointment_date),
                'appointment_time': str(apt.appointment_time),
                'status': apt.status,
            })

        return Response({
            'code': 200,
            'message': '获取看板数据成功',
            'data': {
                'today_appointments': today_appointments,
                'total_income': total_income,
                'good_rate': good_rate,
                'total_services': total_services,
                'total_reviews': total_reviews,
                'recent_appointments': recent_list,
            }
        })


# ========== 时段设置 ==========
from .models import TimeSlot
from rest_framework import serializers as drf_serializers


class TimeSlotSerializer(drf_serializers.ModelSerializer):
    """时段序列化器"""
    day_name = drf_serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'provider', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_available']
        read_only_fields = ['provider']

    def get_day_name(self, obj):
        return obj.get_day_of_week_display()


class TimeSlotListCreateView(generics.ListCreateAPIView):
    """获取/添加时段"""
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimeSlot.objects.filter(provider=self.request.user)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '时段添加成功',
            'data': response.data
        }, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '获取时段列表成功',
            'data': response.data
        })


class TimeSlotDeleteView(generics.DestroyAPIView):
    """删除时段"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimeSlot.objects.filter(provider=self.request.user)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            'code': 200,
            'message': '时段删除成功'
        }, status=status.HTTP_200_OK)


class ServiceUpdateView(generics.GenericAPIView):
    """修改服务信息"""
    permission_classes = [IsAuthenticated]

    def put(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        if service.provider != request.user:
            return Response({'code': 403, 'message': '无权修改'}, status=403)

        for field in ['name', 'description', 'category', 'price', 'duration', 'address']:
            val = request.data.get(field)
            if val is not None:
                setattr(service, field, val)

        image_data = request.data.get('image', '')
        if image_data and image_data.startswith('data:image'):
            url = _save_service_image(request, image_data)
            if url:
                service.image_url = url

        service.save()
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': ServiceSerializer(service, context={'request': request}).data
        })
