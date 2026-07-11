from django.urls import path
from .views import AlipayPayView, AlipayNotifyView, AlipayConfirmView, MockAlipayPayView

urlpatterns = [
    path('alipay/', AlipayPayView.as_view(), name='alipay-pay'),
    path('alipay/notify/', AlipayNotifyView.as_view(), name='alipay-notify'),
    path('alipay/confirm/', AlipayConfirmView.as_view(), name='alipay-confirm'),
    path('mock-pay/', MockAlipayPayView.as_view(), name='mock-pay'),
]
