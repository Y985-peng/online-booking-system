<template>
  <div style="background:#f7f8fa;min-height:100vh;">
    <!-- 视图切换：我的预约 / 服务订单（仅服务提供者可见） -->
    <div style="display:flex;padding:10px;gap:10px;background:#fff;">
      <van-button :type="viewMode === 'my' ? 'primary' : 'default'" size="small" block @click="switchView('my')">我的预约</van-button>
      <van-button v-if="isProvider" :type="viewMode === 'provider' ? 'primary' : 'default'" size="small" block @click="switchView('provider')">服务订单</van-button>
    </div>
    <van-tabs v-model:active="active" @change="(name) => loadOrders(name)">
      <van-tab title="全部" name="" />
      <van-tab title="待支付" name="pending" />
      <van-tab title="已支付" name="paid" />
      <van-tab title="已确认" name="confirmed" />
      <van-tab title="已完成" name="completed" />
      <van-tab title="已取消" name="cancelled" />
    </van-tabs>

    <van-empty v-if="!loading && orders.length === 0" description="暂无预约记录" />
    <van-loading v-if="loading" style="margin-top:50px;" />
    <div style="padding:10px;">
      <van-cell-group inset>
        <van-cell v-for="o in orders" :key="o.id">
          <template #title>
            <div style="font-weight:bold;">{{ o.service_detail?.name || o.service_name || '服务' }}</div>
            <div style="font-size:12px;color:#969799;margin-top:4px;">
              <span v-if="viewMode === 'provider'">{{ o.user_username }} · </span>
              {{ o.appointment_date }} {{ o.appointment_time }}
            </div>
          </template>
          <template #label>
            <div v-if="o.notes" style="font-size:12px;color:#969799;">备注：{{ o.notes }}</div>
          </template>
          <template #value>
            <div style="text-align:right;">
              <div style="color:#ee0a24;font-weight:bold;">¥{{ o.service_detail?.price || 0 }}</div>
              <van-tag :type="statusType(o.status)" style="margin-top:4px;">{{ statusText(o.status) }}</van-tag>
            </div>
          </template>
          <template #extra>
            <!-- 服务提供者视角：确认已支付的预约 -->
            <van-button v-if="viewMode === 'provider' && o.status === 'paid'" size="small" type="primary" style="margin-top:6px;" @click.stop="onConfirm(o.id)">确认预约</van-button>
            <!-- 用户视角：支付/取消 -->
            <van-button v-if="viewMode === 'my' && o.status === 'pending'" size="small" type="warning" plain style="margin-top:6px;" @click.stop="goPay(o)">去支付</van-button>
            <van-button v-if="viewMode === 'my' && o.status !== 'completed' && o.status !== 'cancelled'" size="small" type="danger" plain style="margin-top:6px;margin-left:4px;" @click.stop="onCancel(o.id)">取消</van-button>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- 预约详情弹窗 -->
    <van-dialog v-model:show="showDetail" title="预约详情">
      <div style="padding:20px;">
        <p><strong>服务：</strong>{{ detailOrder.service_detail?.name || detailOrder.service_name }}</p>
        <p><strong>预约者：</strong>{{ detailOrder.user_username }}</p>
        <p><strong>日期：</strong>{{ detailOrder.appointment_date }}</p>
        <p><strong>时间：</strong>{{ detailOrder.appointment_time }}</p>
        <p><strong>价格：</strong>¥{{ detailOrder.service_detail?.price || 0 }}</p>
        <p><strong>状态：</strong>{{ statusText(detailOrder.status) }}</p>
        <p v-if="detailOrder.notes"><strong>备注：</strong>{{ detailOrder.notes }}</p>
        <div style="margin-top:20px;display:flex;gap:10px;">
          <van-button v-if="detailOrder.status === 'paid' && viewMode === 'provider'" type="primary" block @click="onConfirmDetail">确认预约</van-button>
          <van-button v-if="detailOrder.status === 'pending'" type="warning" plain block @click="goPay(detailOrder)">去支付</van-button>
          <van-button v-if="detailOrder.status === 'pending' || detailOrder.status === 'confirmed'" type="danger" plain block @click="onCancelDetail">取消预约</van-button>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../store/user'
import { extractList } from '../utils/data'
import { bookingApi } from '../api'
import request from '../utils/request'
import { showSuccessToast } from 'vant'

const router = useRouter()
const userStore = useUserStore()
const active = ref('')
const orders = ref([])
const loading = ref(false)
const showDetail = ref(false)
const detailOrder = ref({})
const viewMode = ref('my')
const isProvider = computed(() => userStore.userInfo?.role === 'provider')

const switchView = (mode) => {
  viewMode.value = mode
  active.value = ''
  loadOrders()
}


const statusType = (s) => {
  const map = { pending: 'warning', paid: 'success', confirmed: 'primary', completed: 'default', cancelled: 'danger' }
  return map[s] || 'default'
}
const statusText = (s) => {
  const map = { pending: '待支付', paid: '已支付', confirmed: '已确认', completed: '已完成', cancelled: '已取消' }
  return map[s] || s
}

const showOrderDetail = (o) => {
  detailOrder.value = o
  showDetail.value = true
}

const onConfirmDetail = async () => {
  try {
    await bookingApi.confirm(detailOrder.value.id)
    alert('✅ 预约已确认')
    showDetail.value = false
    await loadOrders()
  } catch (e) {
    alert('❌ ' + (e?.response?.data?.message || '确认失败'))
  }
}

const onCancelDetail = async () => {
  try {
    await bookingApi.cancel(detailOrder.value.id)
    alert('预约已取消')
    showDetail.value = false
    await loadOrders()
  } catch (e) {
    alert('❌ ' + (e?.response?.data?.message || '取消失败'))
  }
}

const goPay = async (o) => {
  const name = o.service_detail?.name || o.service_name || '服务预约'
  router.push(`/payment?id=${o.id}&amount=${o.service_detail?.price || 0}&name=${encodeURIComponent(name)}`)
}

const onConfirm = async (id) => {
  try {
    await bookingApi.confirm(id)
    alert('✅ 预约已确认，等待服务完成')
    await loadOrders()
  } catch (e) {
    alert('❌ ' + (e?.response?.data?.message || '确认失败'))
  }
}

const onCancel = async (id) => {
  try {
    await bookingApi.cancel(id)
    alert('预约已取消')
    await loadOrders()
  } catch (e) {
    alert('❌ ' + (e?.response?.data?.message || '取消失败'))
  }
}

const loadOrders = async (tabStatus) => {
  loading.value = true
  try {
    const params = {}
    if (tabStatus || active.value) params.status = tabStatus || active.value
    // 如果是提供者视图，调用提供者接口
    const res = viewMode.value === 'provider'
      ? await request.get('/appointments/provider/', { params })
      : await bookingApi.getList(params)
    orders.value = extractList(res)
  } catch (e) {
    console.error('加载订单失败', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const __route = useRoute()
  // 从支付宝跳转回来时，立即确认支付
  if (__route.query.from_alipay) {
    const tradeNo = __route.query.trade_no || ''
    try {
      await request.post('/payments/alipay/confirm/', { trade_no: tradeNo })
    } catch (e) { /* 超时无所谓，支付宝已确认支付 */ }
    await loadOrders()
  } else {
    await loadOrders()
  }

  await loadOrders()
})
</script>
