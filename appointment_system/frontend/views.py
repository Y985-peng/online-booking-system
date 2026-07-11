import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.views.generic import View

FRONTEND_DIR = os.path.join(settings.BASE_DIR, 'frontend')


class FrontendAppView(View):
    """
    单页应用入口：所有非 API 路径都返回 index.html
    """

    def get(self, request, *args, **kwargs):
        if request.path.startswith('/api/') or request.path.startswith('/admin/'):
            raise Http404
        try:
            return FileResponse(
                open(os.path.join(FRONTEND_DIR, 'index.html'), 'rb'),
                content_type='text/html'
            )
        except FileNotFoundError:
            raise Http404


class FrontendAssetsView(View):
    """
    前端静态资源（JS/CSS/图片）
    """

    def get(self, request, filepath):
        # JS/CSS 在 frontend/assets/ 目录下
        if request.path.startswith('/assets/'):
            file_path = os.path.join(FRONTEND_DIR, 'assets', filepath)
        else:
            # 其它文件（如 favicon.svg）在 frontend/ 根目录
            file_path = os.path.join(FRONTEND_DIR, filepath)

        if not os.path.exists(file_path):
            raise Http404

        ext = os.path.splitext(filepath)[1].lower()
        content_types = {
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.svg': 'image/svg+xml',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.ico': 'image/x-icon',
            '.webp': 'image/webp',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
        }
        content_type = content_types.get(ext, 'application/octet-stream')

        return FileResponse(open(file_path, 'rb'), content_type=content_type)
