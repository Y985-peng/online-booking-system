<template>
  <div style="background:#f7f8fa;min-height:100vh;">
    <van-nav-bar title="收银台" left-arrow @click-left="router.back()" />

    <van-loading v-if="loading" style="margin-top:80px;" />

    <template v-if="!loading">
      <div style="background:#fff;padding:20px;margin:10px;border-radius:8px;">
        <div style="text-align:center;">
          <div style="font-size:24px;color:#ee0a24;font-weight:bold;">¥ {{ amount }}</div>
          <div style="font-size:14px;color:#969799;margin-top:8px;">{{ serviceName }}</div>
        </div>
        <van-divider />
        <div v-if="tradeNo" style="font-size:12px;color:#969799;">交易号：{{ tradeNo }}</div>
      </div>

      <div style="background:#fff;margin:10px;border-radius:8px;overflow:hidden;">
        <div style="padding:15px;font-size:14px;font-weight:bold;border-bottom:1px solid #f5f5f5;">选择支付方式</div>
        <van-radio-group v-model="payMethod">
          <van-cell-group>
            <van-cell clickable @click="payMethod = 'alipay'">
              <template #title>
                <span style="display:flex;align-items:center;gap:8px;">
                  <svg viewBox="0 0 24 24" width="24" height="24" fill="#1677FF"><path d="M21.422 15.358c-3.22-1.386-6.847-2.408-10.052-3.296 1.48-3.109 3.005-6.226 4.407-9.394.758-1.724 1.344-3.598.042-5.455-1.17-1.668-3.542-1.259-5.092-.457-3.114 1.612-5.14 4.925-6.384 8.202-.762 2.008-1.24 4.15-1.57 6.28 2.984.942 6.08 1.618 9.123 2.21-1.616 3.527-3.893 6.744-6.985 9.267-1.34 1.095-1.97 2.382-1.93 4.034.033 1.314.801 2.088 2.308 1.889 2.62-.347 5.013-2.142 6.765-4.041 2.123-2.274 3.89-4.866 5.525-7.492 1.863.569 3.63 1.097 5.387 1.644 1.364.425 2.296-.272 1.942-1.675-.274-1.088-1.588-1.68-2.486-2.116z"/></svg>
                  支付宝
                </span>
              </template>
              <template #right-icon>
                <van-radio name="alipay" />
              </template>
            </van-cell>
          </van-cell-group>
        </van-radio-group>
      </div>

      <div style="margin:30px 16px;">
        <van-button round block type="primary" size="large" :loading="paying" @click="onPay">
          立即支付 · ¥{{ amount }}
        </van-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const paying = ref(false)
const payMethod = ref('alipay')
const appointmentId = ref(null)
const amount = ref('0.00')
const serviceName = ref('')
const tradeNo = ref('')
const payUrl = ref('')
const isMock = ref(false)

onMounted(async () => {
  appointmentId.value = route.query.id
  if (!appointmentId.value) {
    alert('缺少订单信息')
    router.push('/orders')
    return
  }
  try {
    const res = await request.post('/payments/alipay/', {
      appointment_id: appointmentId.value
    })
    const data = res?.data || res
    amount.value = data.amount || route.query.amount || '0.00'
    serviceName.value = data.service_name || route.query.name || '服务预约'
    tradeNo.value = data.trade_no || ''
    payUrl.value = data.pay_url || ''
    isMock.value = data.is_mock !== false
  } catch (e) {
    amount.value = route.query.amount || '0.00'
    serviceName.value = route.query.name || '服务预约'
    isMock.value = true
  } finally {
    loading.value = false
  }
})

const onPay = async () => {
  paying.value = true
  try {
    if (payUrl.value && !isMock.value) {
      window.location.href = payUrl.value
    } else {
      alert('❌ 支付服务暂时不可用，请稍后重试')
    }
  } catch (e) {
    const d = e?.response?.data
    alert('❌ ' + (d?.message || (d?.errors ? JSON.stringify(d.errors) : '支付失败')))
  } finally {
    paying.value = false
  }
}
</script>
