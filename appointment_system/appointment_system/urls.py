from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from frontend.views import FrontendAppView, FrontendAssetsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/services/', include('services.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/posts/', include('posts.urls')),
    # 前端静态资源
    path('assets/<path:filepath>', FrontendAssetsView.as_view(), name='frontend-assets'),
    path('favicon.svg', FrontendAssetsView.as_view(), {'filepath': 'favicon.svg'}, name='favicon'),
    path('manifest.json', FrontendAssetsView.as_view(), {'filepath': 'manifest.json'}, name='manifest'),
    # 前端 SPA 入口（所有非 API 路径）
    path('', FrontendAppView.as_view(), name='frontend-index'),
    path('<path:path>', FrontendAppView.as_view(), name='frontend-spa'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
