import json, uuid, logging
from datetime import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from appointments.models import Appointment
from .alipay import AlipayClient

logger = logging.getLogger(__name__)


def generate_trade_no():
    """生成支付宝交易号"""
    date_part = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"BK{date_part}{uuid.uuid4().hex[:8].upper()}"


class AlipayPayView(generics.GenericAPIView):
    """
    支付宝支付接口
    POST /api/payments/alipay/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        if not appointment_id:
            return Response({'code': 400, 'message': '缺少预约ID'}, status=400)

        appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

        if appointment.status != 'pending':
            return Response({'code': 400, 'message': '该预约状态不允许支付'}, status=400)

        amount = float(appointment.service.price)
        trade_no = generate_trade_no()

        # 保存交易号到预约记录
        appointment.payment_trade_no = trade_no
        appointment.notes = (appointment.notes or '') + f"\n[trade_no:{trade_no}]"
        appointment.save(update_fields=['payment_trade_no', 'notes'])

        # 生成支付宝支付链接（如果配了密钥）
        client = AlipayClient({
            'app_id': getattr(settings, 'ALIPAY_APP_ID', ''),
            'app_private_key': getattr(settings, 'ALIPAY_APP_PRIVATE_KEY', ''),
            'alipay_public_key': getattr(settings, 'ALIPAY_PUBLIC_KEY', ''),
            'debug': True,
        })

        # 支付宝跳转回前端，异步通知发到后端
        backend_base = "https://yunshenwanli.pythonanywhere.com"
        frontend_base = "https://stirring-pavlova-203f64.netlify.app"
        pay_url = client.get_pay_url(
            out_trade_no=trade_no,
            total_amount=amount,
            subject=f"预约服务 - {appointment.service.name}",
            return_url=f"{frontend_base}/orders?from_alipay=1&trade_no={trade_no}",
            notify_url=f"{backend_base}/api/payments/alipay/notify/",
        )

        return Response({
            'code': 200,
            'message': '获取支付信息成功',
            'data': {
                'appointment_id': appointment.id,
                'trade_no': trade_no,
                'amount': amount,
                'service_name': appointment.service.name,
                'pay_url': pay_url,
                'is_mock': pay_url is None,
            }
        })


class AlipayNotifyView(generics.GenericAPIView):
    """
    支付宝异步通知接口
    支付成功后支付宝会自动调用这个地址
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        logger.info(f"支付宝异步通知: {request.data}")
        try:
            trade_no = request.data.get('out_trade_no', '')
            trade_status = request.data.get('trade_status', '')

            if trade_status == 'TRADE_SUCCESS':
                # 从预约备注中提取交易号，标记为已支付
                from appointments.models import Appointment
                appointments = Appointment.objects.filter(Q(payment_trade_no=trade_no) | Q(notes__contains=trade_no))
                for apt in appointments:
                    if apt.status == 'pending':
                        apt.status = 'paid'
                        apt.save(update_fields=['status', 'updated_at'])
                        logger.info(f"预约 #{apt.id} 已通过支付宝通知标记为已支付")
        except Exception as e:
            logger.error(f"处理支付宝通知失败: {e}")

        return Response('success')


class MockAlipayPayView(generics.GenericAPIView):
    """
    模拟支付宝支付
    POST /api/payments/mock-pay/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        if not appointment_id:
            return Response({'code': 400, 'message': '缺少预约ID'}, status=400)

        appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

        if appointment.status != 'pending':
            return Response({'code': 400, 'message': '该预约状态不允许支付'}, status=400)

        appointment.status = 'paid'
        appointment.save(update_fields=['status', 'updated_at'])

        return Response({
            'code': 200,
            'message': '支付成功',
            'data': {
                'id': appointment.id,
                'status': 'paid',
                'service_name': appointment.service.name,
                'amount': float(appointment.service.price),
            }
        })


class AlipayConfirmView(generics.GenericAPIView):
    """
    支付宝支付确认接口（用户从支付宝跳转回来后调用）
    POST /api/payments/alipay/confirm/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        trade_no = request.data.get('trade_no')
        appointment_id = request.data.get('appointment_id')

        from appointments.models import Appointment

        # 优先用交易号查找
        if trade_no:
            appointments = Appointment.objects.filter(Q(payment_trade_no=trade_no) | Q(notes__contains=trade_no), user=request.user)
        elif appointment_id:
            appointments = Appointment.objects.filter(id=appointment_id, user=request.user)
        else:
            return Response({'code': 400, 'message': '缺少交易号或预约ID'}, status=400)

        for apt in appointments:
            if apt.status == 'pending':
                apt.status = 'paid'
                apt.save(update_fields=['status', 'updated_at'])
                return Response({
                    'code': 200,
                    'message': '支付确认成功',
                    'data': {'id': apt.id, 'status': 'paid'}
                })

        if appointments:
            apt = appointments.first()
            return Response({
                'code': 200,
                'message': '订单已是支付状态',
                'data': {'id': apt.id, 'status': apt.status}
            })

        return Response({'code': 404, 'message': '未找到对应订单'}, status=404)
