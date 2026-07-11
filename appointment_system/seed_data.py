#!/usr/bin/env python3
"""
测试数据填充脚本
运行方式: python3 seed_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Service, ServiceCategory, TimeSlot
from reviews.models import Review

User = get_user_model()


def create_users():
    """创建测试用户"""
    users_data = [
        {'username': 'alice', 'password': 'test123', 'role': 'provider', 'phone': '13800138001'},
        {'username': 'bob', 'password': 'test123', 'role': 'provider', 'phone': '13800138002'},
        {'username': 'carol', 'password': 'test123', 'role': 'user', 'phone': '13800138003'},
        {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'phone': ''},
        {'username': '云深', 'password': '111111', 'role': 'user', 'phone': ''},
        {'username': '张三', 'password': '111111', 'role': 'user', 'phone': ''},
        {'username': 'david', 'password': 'test123', 'role': 'provider', 'phone': '13800138004'},
        {'username': 'ella', 'password': 'test123', 'role': 'provider', 'phone': '13800138005'},
        {'username': 'frank', 'password': 'test123', 'role': 'user', 'phone': '13800138006'},
        {'username': 'grace', 'password': 'test123', 'role': 'user', 'phone': '13800138007'},
    ]
    created = []
    for data in users_data:
        user, flag = User.objects.get_or_create(
            username=data['username'],
            defaults={'role': data['role'], 'phone': data['phone']}
        )
        if flag:
            user.set_password(data['password'])
            user.save()
            print(f'  ✓ 创建用户: {data["username"]} ({data["role"]})')
        created.append(user)
    return created


def create_categories():
    """创建服务分类"""
    categories = ['医疗', '健身', '美容', '家政', '维修', '摄影', '设计', '法律', '翻译', '家教']
    created = []
    for name in categories:
        cat, flag = ServiceCategory.objects.get_or_create(name=name)
        if flag:
            print(f'  ✓ 创建分类: {name}')
        created.append(cat)
    return created


def create_services(providers):
    """创建测试服务"""
    services_data = [
        {'provider': providers[0], 'name': '中医推拿理疗', 'category': '医疗', 'price': 199, 'duration': 60,
         'address': '武汉市洪山区珞喻路1037号', 'description': '专业中医推拿，疏通经络，缓解疲劳。服务包括背部推拿、肩颈按摩、头部放松等。'},
        {'provider': providers[0], 'name': '针灸调理', 'category': '医疗', 'price': 150, 'duration': 45,
         'address': '武汉市洪山区珞喻路1037号', 'description': '传统针灸疗法，调理气血，改善亚健康状态。'},
        {'provider': providers[1], 'name': '面部深层清洁', 'category': '美容', 'price': 299, 'duration': 90,
         'address': '武汉市武昌区楚河汉街', 'description': '深层清洁毛孔，去除黑头粉刺，配合补水面膜，让肌肤焕然一新。'},
        {'provider': providers[1], 'name': '健身私教课', 'category': '健身', 'price': 399, 'duration': 60,
         'address': '武汉市江岸区中山大道', 'description': '一对一专业私教指导，定制个性化健身计划，包含力量训练和有氧运动。'},
        {'provider': providers[0], 'name': '高中数学家教', 'category': '家教', 'price': 200, 'duration': 120,
         'address': '线上授课', 'description': '985高校数学专业，5年家教经验，擅长高中数理化辅导。'},
        {'provider': providers[1], 'name': '全屋深度清洁', 'category': '家政', 'price': 299, 'duration': 180,
         'address': '武汉市洪山区', 'description': '专业家政团队，全屋深度清洁，包含厨房、卫生间、卧室、客厅。'},
        {'provider': providers[0], 'name': '水电维修', 'category': '维修', 'price': 100, 'duration': 60,
         'address': '武汉市武昌区', 'description': '专业水电工，上门维修，包含水管、电路、灯具、开关等。'},
        {'provider': providers[1], 'name': '个人写真摄影', 'category': '摄影', 'price': 599, 'duration': 120,
         'address': '武汉市江汉区', 'description': '专业摄影师，提供个人写真、情侣照、全家福拍摄服务。'},
        {'provider': providers[0], 'name': 'Logo设计', 'category': '设计', 'price': 500, 'duration': 0,
         'address': '线上服务', 'description': '资深设计师，提供Logo、海报、名片等平面设计服务。'},
        {'provider': providers[1], 'name': '法律咨询', 'category': '法律', 'price': 300, 'duration': 60,
         'address': '武汉市江岸区', 'description': '执业律师提供专业法律咨询服务，包含合同审查、纠纷解决等。'},
        {'provider': providers[0], 'name': '中英翻译', 'category': '翻译', 'price': 200, 'duration': 0,
         'address': '线上服务', 'description': '专业翻译，中英文互译，包含文档翻译、口译服务。'},
        {'provider': providers[2], 'name': '颈椎康复理疗', 'category': '医疗', 'price': 180, 'duration': 60,
         'address': '武汉市洪山区鲁巷', 'description': '专业颈椎康复理疗，针对长期伏案工作导致的颈椎问题。'},
        {'provider': providers[2], 'name': '中医拔罐刮痧', 'category': '医疗', 'price': 120, 'duration': 45,
         'address': '武汉市洪山区鲁巷', 'description': '传统拔罐刮痧，祛湿排毒，缓解肌肉酸痛。'},
        {'provider': providers[3], 'name': '韩式半永久纹眉', 'category': '美容', 'price': 888, 'duration': 120,
         'address': '武汉市武昌区中南路', 'description': '韩式半永久纹眉，自然仿真，持久不褪色。'},
        {'provider': providers[3], 'name': '美甲美睫套餐', 'category': '美容', 'price': 199, 'duration': 90,
         'address': '武汉市武昌区中南路', 'description': '精致美甲+自然美睫套餐，多种风格可选。'},
        {'provider': providers[2], 'name': '瑜伽私教课', 'category': '健身', 'price': 299, 'duration': 60,
         'address': '武汉市江汉区武广', 'description': '专业瑜伽教练一对一指导，包含哈他瑜伽、流瑜伽等。'},
        {'provider': providers[3], 'name': '减脂塑形训练', 'category': '健身', 'price': 499, 'duration': 90,
         'address': '武汉市江汉区武广', 'description': '科学减脂塑形训练，含体测和饮食指导。'},
        {'provider': providers[2], 'name': '英语口语陪练', 'category': '家教', 'price': 150, 'duration': 60,
         'address': '线上授课', 'description': '专业英语老师，一对一英语口语陪练，提升口语表达能力。'},
        {'provider': providers[3], 'name': '钢琴启蒙教学', 'category': '家教', 'price': 200, 'duration': 60,
         'address': '武汉市洪山区街道口', 'description': '钢琴专业教师，儿童钢琴启蒙教育，寓教于乐。'},
        {'provider': providers[2], 'name': '日常保洁服务', 'category': '家政', 'price': 150, 'duration': 120,
         'address': '武汉市武昌区', 'description': '日常家庭保洁，含扫地拖地、擦窗、厨房清洁等。'},
        {'provider': providers[3], 'name': '家电清洗维修', 'category': '维修', 'price': 120, 'duration': 60,
         'address': '武汉市洪山区', 'description': '空调、洗衣机、冰箱等家电清洗和维修服务。'},
        {'provider': providers[2], 'name': '婚纱摄影', 'category': '摄影', 'price': 2999, 'duration': 480,
         'address': '武汉市东湖风景区', 'description': '专业婚纱摄影团队，含外景拍摄、精修照片等。'},
        {'provider': providers[3], 'name': 'UI界面设计', 'category': '设计', 'price': 800, 'duration': 0,
         'address': '线上服务', 'description': '资深UI设计师，提供APP、网页界面设计服务。'},
        {'provider': providers[2], 'name': '合同审核起草', 'category': '法律', 'price': 500, 'duration': 0,
         'address': '线上服务', 'description': '专业律师审核起草各类合同，包含劳动、买卖、租赁合同等。'},
        {'provider': providers[3], 'name': '日语翻译', 'category': '翻译', 'price': 250, 'duration': 0,
         'address': '线上服务', 'description': '专业日语翻译，中日互译，包含商务、技术文档翻译。'},
    ]
    services = []
    for data in services_data:
        service, flag = Service.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        services.append(service)
    return services


def create_reviews(users, services):
    """创建测试评价"""
    reviews_data = [
        {'user': users[2], 'service': services[0], 'rating': 5, 'content': '非常专业的推拿服务，做完后整个人轻松了很多！'},
        {'user': users[2], 'service': services[1], 'rating': 4, 'content': '针灸效果不错，就是稍微有点疼。'},
        {'user': users[2], 'service': services[2], 'rating': 5, 'content': '清洁效果很好，皮肤感觉变白了很多。'},
    ]
    for data in reviews_data:
        _, flag = Review.objects.get_or_create(
            user=data['user'],
            service=data['service'],
            defaults={'rating': data['rating'], 'content': data['content']}
        )
        if flag:
            print(f'  ✓ 创建评价: {data["user"].username} → {data["service"].name} ({data["rating"]}星)')

    # 更新服务评分
    for service in services:
        from django.db.models import Avg, Count
        result = Review.objects.filter(service=service).aggregate(
            avg_rating=Avg('rating'), count=Count('id')
        )
        service.rating = round(result['avg_rating'] or 0, 1)
        service.review_count = result['count'] or 0
        service.save(update_fields=['rating', 'review_count'])


def create_time_slots(providers):
    """创建测试时段"""
    slots_data = [
        {'provider': providers[0], 'day_of_week': 'monday', 'start_time': '09:00', 'end_time': '18:00'},
        {'provider': providers[0], 'day_of_week': 'tuesday', 'start_time': '09:00', 'end_time': '18:00'},
        {'provider': providers[0], 'day_of_week': 'wednesday', 'start_time': '09:00', 'end_time': '18:00'},
        {'provider': providers[0], 'day_of_week': 'thursday', 'start_time': '09:00', 'end_time': '18:00'},
        {'provider': providers[0], 'day_of_week': 'friday', 'start_time': '09:00', 'end_time': '18:00'},
        {'provider': providers[1], 'day_of_week': 'monday', 'start_time': '10:00', 'end_time': '20:00'},
        {'provider': providers[1], 'day_of_week': 'wednesday', 'start_time': '10:00', 'end_time': '20:00'},
        {'provider': providers[1], 'day_of_week': 'friday', 'start_time': '10:00', 'end_time': '20:00'},
        {'provider': providers[1], 'day_of_week': 'saturday', 'start_time': '10:00', 'end_time': '17:00'},
    ]
    for data in slots_data:
        _, flag = TimeSlot.objects.get_or_create(
            provider=data['provider'],
            day_of_week=data['day_of_week'],
            start_time=data['start_time'],
            defaults={'end_time': data['end_time']}
        )
        if flag:
            print(f'  ✓ 创建时段: {data["provider"].username} {data["day_of_week"]} {data["start_time"]}-{data["end_time"]}')


if __name__ == '__main__':
    print('=' * 50)
    print('📦 开始填充测试数据...')
    print('=' * 50)

    print('\n👤 创建用户:')
    users = create_users()

    print('\n📋 创建分类:')
    create_categories()
    print('\n📋 创建服务:')
    providers = [u for u in users if u.role == 'provider']
    services = create_services(providers)

    print('\n⭐ 创建评价:')
    create_reviews(users, services)

    print('\n⏰ 创建时段:')
    create_time_slots(providers)

    print('\n' + '=' * 50)
    print('✅ 测试数据填充完成!')
    print('=' * 50)
    print(f'\n测试账号:')
    print(f'  服务提供者: alice / test123')
    print(f'  服务提供者: bob / test123')
    print(f'  普通用户:   carol / test123')
    print(f'  管理员:     admin / admin123')
    print(f'  服务提供者: david / test123')
    print(f'  服务提供者: ella / test123')
    print(f'  普通用户:   frank / test123')
    print(f'  普通用户:   grace / test123')
    print(f'\n启动后端: python3 manage.py runserver 8080')
    print(f'启动前端: cd ../booking-system && npm run dev')
