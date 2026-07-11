<template>
  <div style="padding:15px;background:#f7f8fa;min-height:100vh;">
    <div style="display:flex;padding:0 0 10px;gap:10px;">
      <van-button :type="tabActive === 'write' ? 'primary' : 'default'" size="small" block @click="tabActive = 'write'">发布评价</van-button>
      <van-button v-if="isProvider" :type="tabActive === 'received' ? 'primary' : 'default'" size="small" block @click="tabActive = 'received'">收到的评价</van-button>
    </div>

    <!-- 🔵 发布评价 -->
    <template v-if="tabActive === 'write'">
    <!-- 发布评价 -->
    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field label="关联服务" is-link readonly :model-value="selectedService?.name || '请选择服务'" @click="showServicePicker = true" />
        <van-field label="评分">
          <template #input><van-rate v-model="form.rating" /></template>
        </van-field>
        <van-field v-model="form.content" label="评价内容" type="textarea" rows="4" placeholder="请输入您的评价..." :rules="[{ required: true, message: '请填写评价内容' }]" />
      </van-cell-group>
      <div style="margin:16px;">
        <van-button round block type="primary" native-type="submit" :loading="submitting">提交评价</van-button>
      </div>
    </van-form>

    <!-- 服务选择器 -->
    <van-popup v-model:show="showServicePicker" position="bottom" round :style="{ height: '50vh' }">
      <div style="padding:20px;">
        <h3 style="text-align:center;margin:0 0 15px;">选择已完成的服务</h3>
        <van-cell-group>
          <van-cell v-for="s in myServices" :key="s.id" :title="s.name" is-link @click="selectService(s)" />
        </van-cell-group>
        <van-empty v-if="myServices.length === 0" description="暂无已完成的服务" />
        <van-button plain block style="margin-top:15px;" @click="showServicePicker = false">取消</van-button>
      </div>
    </van-popup>

    <van-divider />

    <!-- 我的评价 -->
    <h3 style="margin:0 0 10px;">我发布的评价</h3>
    <van-empty v-if="myReviews.length === 0" description="暂无评价" />
    <van-cell v-for="r in myReviews" :key="r.id" :title="r.service_name" :label="r.content" style="font-size:14px;">
      <template #value>
        <van-rate v-model="r.rating" :size="14" readonly />
      </template>
    </van-cell>
    </template>

    <!-- 🟢 收到的评价 -->
    <template v-if="tabActive === 'received'">
      <h3 style="margin:0 0 10px;">用户对我的评价</h3>
      <van-empty v-if="receivedReviews.length === 0" description="暂无评价" />
      <van-cell v-for="r in receivedReviews" :key="r.id">
        <template #title>
          <span>{{ r.service_name }}</span>
          <span style="font-size:12px;color:#969799;margin-left:6px;">by {{ r.username }}</span>
        </template>
        <template #label>
          {{ r.content }}
        </template>
        <template #value>
          <van-rate v-model="r.rating" :size="14" readonly />
        </template>
      </van-cell>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../store/user'
import { reviewApi, serviceApi, bookingApi } from '../api'
import { extractList } from '../utils/data'

const userStore = useUserStore()
const isProvider = userStore.userInfo?.role === 'provider'
const tabActive = ref('write')
const form = ref({ service: '', rating: 5, content: '' })
const submitting = ref(false)
const showServicePicker = ref(false)
const selectedService = ref(null)
const myServices = ref([])
const myReviews = ref([])
const receivedReviews = ref([])

const loadCompletedAppointments = async () => {
  try {
    const res = await bookingApi.getList({ status: 'completed' })
    const list = extractList(res)
    myServices.value = list.map(a => ({
      id: a.service_detail?.id || a.service,
      name: a.service_detail?.name || a.service_name || '已完成服务',
      appointment_id: a.id,
      appointment_date: a.appointment_date,
      appointment_time: a.appointment_time,
    }))
  } catch (e) {
    console.error('加载已完成订单失败', e)
  }
  // 后备
  if (myServices.value.length === 0) {
    try {
      const res = await serviceApi.getList({})
      myServices.value = extractList(res).map(s => ({ id: s.id, name: s.name }))
    } catch(e2) {}
  }
}

const loadMyReviews = async () => {
  try {
    if (myServices.value.length > 0) {
      const all = []
      for (const s of myServices.value) {
        const res = await reviewApi.getList(s.id)
        const data = res.data?.results || res.data || []
        all.push(...data)
      }
      myReviews.value = all.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    }
  } catch (e) {
    console.error('加载评价失败', e)
  }
}

const loadReceivedReviews = async () => {
  try {
    const res = await serviceApi.getMyServices()
    const services = extractList(res)
    const all = []
    for (const s of services) {
      const res2 = await reviewApi.getList(s.id)
      const data = res2.data?.results || res2.results || res2.data || res2
      if (Array.isArray(data)) {
        all.push(...data.map(r => ({ ...r, service_name: s.name })))
      }
    }
    receivedReviews.value = all.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (e) {
    console.error('加载收到的评价失败', e)
  }
}

const selectService = (s) => {
  selectedService.value = s
  form.value.appointment = s.appointment_id || null
  form.value.service = s.id
  showServicePicker.value = false
}

const onSubmit = async () => {
  if (!form.value.service) {
    alert('请选择服务')
    return
  }
  submitting.value = true
  try {
    const d = {
      service: form.value.service,
      rating: form.value.rating,
      content: form.value.content,
    }
    if (form.value.appointment) d.appointment = form.value.appointment
    const res = await reviewApi.create(d)
    alert('评价提交成功！')
    form.value = { service: '', rating: 5, content: '', appointment: null }
    selectedService.value = null
    await loadMyReviews()
    await loadReceivedReviews()
  } catch (e) {
    const msg = e?.response?.data?.message || (e?.response?.data?.errors ? JSON.stringify(e.response.data.errors) : '评价提交失败')
    alert('❌ ' + msg)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCompletedAppointments()
  loadMyReviews()
  if (isProvider) loadReceivedReviews()
})
</script>
