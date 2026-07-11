# 预约服务系统 - 后端

基于 Django REST Framework 的预约服务管理系统。

## 目录结构

```
appointment_system/
├── users/           # 用户管理（另一位同学完成）
│   ├── models.py    # 自定义User模型（role: user/provider）
│   ├── serializers.py
│   ├── views.py     # 注册
│   └── urls.py      # /api/auth/register, /api/auth/login
│
├── services/        # 服务管理（另一位同学完成+我扩展）
│   ├── models.py    # Service + TimeSlot（我新增）
│   ├── serializers.py
│   ├── views.py     # 列表/详情/发布/管理/看板/时段（我扩展）
│   └── urls.py      # 所有服务相关API（我扩展）
│
├── appointments/    # 预约管理（另一位同学完成）
│   ├── models.py
│   ├── serializers.py
│   ├── views.py     # 创建/取消/我的预约
│   └── urls.py
│
├── reviews/         # ⭐ 评价管理（我独立完成）
│   ├── models.py    # Review 模型
│   ├── serializers.py
│   ├── views.py     # 创建评价/查看服务评价
│   └── urls.py      # /api/reviews/
│
└── seed_data.py     # ⭐ 测试数据填充脚本（我新增）
```

## 我完成的部分

### 1. 评价系统（全栈）
- **后端**: `reviews/` 完整 CRUD API，创建评价后自动更新服务评分
- **前端**: `Review.vue` 评价发布/展示

### 2. 服务发布与管理
- **后端**: `POST /api/services/publish/` 发布服务
- **后端**: `GET /api/services/my/` 我的服务列表
- **后端**: `PUT/DELETE /api/services/{id}/manage/` 更新/删除服务
- **前端**: `Publish.vue` 发布/管理界面

### 3. 服务提供者时段设置
- **后端**: TimeSlot 模型 + `GET/POST /api/services/time-slots/`
- **前端**: `TimeSettings.vue` 时段管理界面

### 4. 管理看板
- **后端**: `GET /api/services/dashboard/` 统计接口
- **前端**: `Dashboard.vue` 看板展示

### 5. 所有前端页面对接
- 10 个页面全部从模拟数据改造为真实 API 调用
- axios + JWT 认证 + 登录/注册

### 6. 测试
- `reviews/tests.py` - 评价系统单元测试（7个用例）
- `services/tests.py` - 服务发布/时段设置测试（6个用例）

### 7. 测试数据
- `seed_data.py` - 一键填充测试数据的脚本

## API 端点总览

| 方法 | 路径 | 说明 | 需要登录 |
|------|------|------|---------|
| POST | /api/auth/login | 登录获取JWT | ❌ |
| POST | /api/auth/register | 注册 | ❌ |
| GET | /api/services/ | 服务列表（搜索/分类/分页）| ❌ |
| GET | /api/services/{id}/ | 服务详情 | ❌ |
| POST | /api/services/publish/ | 发布服务 | ✅ |
| GET | /api/services/my/ | 我的服务 | ✅ |
| PUT | /api/services/{id}/manage/ | 更新服务 | ✅ |
| DELETE | /api/services/{id}/manage/ | 删除服务 | ✅ |
| GET | /api/services/dashboard/ | 看板统计 | ✅ |
| GET | /api/services/categories/ | 分类列表 | ❌ |
| GET | /api/services/time-slots/ | 时段列表 | ✅ |
| POST | /api/services/time-slots/ | 添加时段 | ✅ |
| DELETE | /api/services/time-slots/{id}/ | 删除时段 | ✅ |
| POST | /api/appointments/ | 创建预约 | ✅ |
| GET | /api/appointments/my/ | 我的预约 | ✅ |
| POST | /api/appointments/{id}/cancel/ | 取消预约 | ✅ |
| POST | /api/reviews/ | 创建评价 | ✅ |
| GET | /api/reviews/service/{id}/ | 服务评价列表 | ❌ |

## 快速启动

```bash
# 1. 后端
cd appointment_system
pip3 install django djangorestframework djangorestframework-simplejwt
python3 manage.py migrate
python3 manage.py runserver 8080

# 2. 填充测试数据（可选）
python3 seed_data.py

# 3. 前端（新开终端）
cd ../booking-system
npm install
npm run dev
```

## 测试

```bash
cd appointment_system
python3 manage.py test reviews services
```

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 服务提供者 | alice | test123 |
| 服务提供者 | bob | test123 |
| 普通用户 | carol | test123 |
