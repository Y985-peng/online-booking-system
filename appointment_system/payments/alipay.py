"""
支付宝沙箱支付集成模块

使用方式：
1. 前往 https://open.alipay.com 注册开发者账号
2. 进入沙箱环境 (https://open.alipay.com/develop/sandbox)
3. 获取 APP_ID, 生成 RSA2 密钥
4. 将配置填入 appointment_system/settings.py

本地测试无需真实密钥，系统会自动使用模拟模式。
"""

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AlipayClient:
    """支付宝支付客户端（含沙箱模式）"""

    def __init__(self, config=None):
        self.config = config or {}
        self.sandbox = not self._is_configured()

    def _is_configured(self):
        """检查是否配置了真实的支付宝密钥"""
        return bool(
            self.config.get('app_id')
            and self.config.get('app_private_key')
            and self.config.get('alipay_public_key')
        )

    def get_pay_url(self, out_trade_no, total_amount, subject, return_url, notify_url):
        """
        获取支付宝支付链接
        
        如果未配置真实密钥，返回模拟支付页面 URL
        """
        if not self._is_configured():
            logger.info(f"[支付宝模拟] 订单 {out_trade_no} - ¥{total_amount}")
            return None  # 表示使用模拟模式

        try:
            from alipay import AliPay, AliPayConfig

            alipay = AliPay(
                appid=self.config['app_id'],
                app_notify_url=notify_url,
                app_private_key_string=self.config['app_private_key'],
                alipay_public_key_string=self.config['alipay_public_key'],
                sign_type="RSA2",
                debug=self.config.get('debug', True),
                config=AliPayConfig(timeout=15),
            )

            order_string = alipay.api_alipay_trade_wap_pay(
                out_trade_no=out_trade_no,
                total_amount=float(total_amount),
                subject=subject,
                return_url=return_url,
                notify_url=notify_url,
            )

            gateway = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
            pay_url = f"{gateway}?{order_string}"
            return pay_url

        except ImportError:
            logger.warning("python-alipay-sdk 未安装，使用模拟模式")
            return None
        except Exception as e:
            logger.error(f"支付宝支付链接生成失败: {e}")
            return None


# 全局实例
alipay_client = AlipayClient()
