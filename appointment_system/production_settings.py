"""部署到 PythonAnywhere 时用这个 settings"""
from .settings import *

# 1. 改成你的 PythonAnywhere 用户名
ALLOWED_HOSTS = ['你的用户名.pythonanywhere.com']

# 2. 关闭调试模式
DEBUG = False

# 3. 静态文件配置
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# 4. 数据库 - PythonAnywhere 上推荐用 MySQL（免费版用 SQLite 也行）
# SQLite（免费版用这个）:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 5. CORS 设置 - 允许 APK 跨域请求
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
CORS_ALLOW_ALL_ORIGINS = True

# 6. CSRF 信任来源
CSRF_TRUSTED_ORIGINS = ['https://你的用户名.pythonanywhere.com']
