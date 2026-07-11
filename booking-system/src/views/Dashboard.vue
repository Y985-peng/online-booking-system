<template>
  <div style="background:#f7f8fa;min-height:100vh;padding-top:10px;">
    <h2 style="padding:0 15px;">管理看板</h2>

    <van-grid :column-num="3" :border="false" style="margin:10px;">
      <van-grid-item icon="orders-o" :text="'今日预约 (' + stats.today_appointments + ')'" />
      <van-grid-item icon="cash-back-record" :text="'本月收入 (¥' + stats.total_income + ')'" />
      <van-grid-item icon="comment-o" :text="'好评率 (' + stats.good_rate + '%)'" />
    </van-grid>

    <van-cell-group inset style="margin:10px;">
      <van-cell title="我的服务数" :value="stats.total_services + ' 个'" />
      <van-cell title="总评价数" :value="stats.total_reviews + ' 条'" />
    </van-cell-group>

    <van-cell-group inset style="margin:10px;">
      <van-cell title="近期预约" />
      <van-cell v-for="apt in stats.recent_appointments" :key="apt.id" :title="apt.username" :label="apt.appointment_date + ' ' + apt.appointment_time + ' ' + apt.service_name">
        <template #value>
          <van-tag :type="statusType(apt.status)">{{ statusText(apt.status) }}</van-tag>
        </template>
      </van-cell>
      <van-empty v-if="stats.recent_appointments.length === 0" description="暂无预约" style="padding:20px;" />
    </van-cell-group>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { extractData } from '../utils/data'
import { dashboardApi } from '../api'

const stats = ref({
  today_appointments: 0,
  total_income: 0,
  good_rate: 100,
  total_services: 0,
  total_reviews: 0,
  recent_appointments: [],
})

const statusType = (s) => {
  const map = { pending: 'warning', confirmed: 'primary', completed: 'success', cancelled: 'danger' }
  return map[s] || 'default'
}
const statusText = (s) => {
  const map = { pending: '待确认', confirmed: '已确认', completed: '已完成', cancelled: '已取消' }
  return map[s] || s
}

const loadStats = async () => {
  try {
    const res = await dashboardApi.getStats()
    stats.value = extractData(res) || stats.value
  } catch (e) {
    console.error('加载看板数据失败', e)
  }
}

onMounted(loadStats)
</script>
