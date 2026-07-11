<template>
  <div style="padding:0;background:#f7f8fa;min-height:100vh;">
    <van-nav-bar title="预约下单" left-arrow @click-left="router.back()" />
    <div style="padding:20px;">
      <van-form @submit="onSubmit">
        <van-cell-group inset>
          <van-cell title="服务" :value="serviceName" />
          <van-cell title="日期" is-link :value="form.date || '请选择日期'" @click="showDatePicker = true" />
          <van-cell title="时段" is-link :value="form.time || '请选择时段'" @click="showTimePicker = true" />
          <van-cell v-if="workHoursInfo" title="工作时段" :value="workHoursInfo" />
          <van-field v-model="form.notes" label="备注" placeholder="可选填备注信息" />
        </van-cell-group>
        <div style="margin-top:20px;">
          <van-button round block type="primary" native-type="submit" :loading="submitting">确认预约</van-button>
        </div>
      </van-form>
    </div>
    <van-popup v-model:show="showDatePicker" position="bottom" :style="{height:'40vh'}">
      <van-date-picker title="选择日期" :min-date="minDate" @confirm="onDateConfirm" @cancel="showDatePicker = false" />
    </van-popup>
    <van-popup v-model:show="showTimePicker" position="bottom" :style="{height:'40vh'}">
      <van-time-picker title="选择时段" @confirm="onTimeConfirm" @cancel="showTimePicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '../utils/request'
import { bookingApi } from '../api'

const route = useRoute()
const router = useRouter()
const submitting = ref(false)
const showDatePicker = ref(false)
const showTimePicker = ref(false)
const minDate = new Date()
const workStart = ref('')
const workEnd = ref('')
const svcDuration = ref(0)

const workHoursInfo = computed(() => {
  if (workStart.value && workEnd.value) {
    return '工作时段: ' + workStart.value + ' - ' + workEnd.value
  }
  return ''
})

const validateTime = (timeStr) => {
  if (!workStart.value || !workEnd.value) return { ok: true }
  const [h, m] = timeStr.split(':').map(Number)
  const startMins = h * 60 + m
  const [wsH, wsM] = workStart.value.split(':').map(Number)
  const [weH, weM] = workEnd.value.split(':').map(Number)
  const wsMins = wsH * 60 + wsM
  const weMins = weH * 60 + weM
  const endMins = startMins + svcDuration.value
  if (startMins < wsMins) return { ok: false, msg: '当前非工作时段，工作时段为 ' + workStart.value + ' - ' + workEnd.value }
  if (endMins > weMins) return { ok: false, msg: '预约时间超出工作时段（服务时长' + svcDuration.value + '分钟），最晚可预约 ' + workEnd.value }
  return { ok: true }
}

const serviceId = ref(null)
const serviceName = ref('')
const servicePrice = ref(0)

const form = ref({ service: null, date: '', time: '', notes: '' })

const onDateConfirm = ({ selectedValues }) => {
  form.value.date = selectedValues.join('-')
  showDatePicker.value = false
}
const onTimeConfirm = ({ selectedValues }) => {
  if (selectedValues && selectedValues.length >= 2) {
    form.value.time = selectedValues[0] + ':' + selectedValues[1]
  }
  showTimePicker.value = false
}

const onSubmit = async () => {
  if (!form.value.date) { alert('请选择日期'); return }
  if (!form.value.time) { alert('请选择时段'); return }
  const timeCheck = validateTime(form.value.time)
  if (!timeCheck.ok) { alert('❌ ' + timeCheck.msg); return }
  submitting.value = true
  try {
    const res = await bookingApi.create({ service: serviceId.value, appointment_date: form.value.date, appointment_time: form.value.time, notes: form.value.notes })
    const aptId = res?.data?.id || res?.id
    if (aptId) {
      alert('✅ 预约成功，请完成支付')
      router.push(`/payment?id=${aptId}&amount=${servicePrice.value}&name=${encodeURIComponent(serviceName.value)}`)
    } else {
      alert('✅ 预约成功')
      router.push('/orders')
    }
  } catch (e) {
    const d = e?.response?.data
    let msg = '预约失败'
    if (d?.message) msg = d.message
    else if (d?.detail) msg = d.detail
    else if (d?.non_field_errors) msg = d.non_field_errors.join('；')
    else if (d?.errors) {
      if (typeof d.errors === 'string') msg = d.errors
      else if (d.errors.appointment_date) msg = d.errors.appointment_date.join('；')
      else msg = JSON.stringify(d.errors)
    }
    else if (e?.message) msg = e.message
    alert('❌ ' + msg)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
  serviceId.value = route.query.service
  serviceName.value = route.query.name || '请先选择服务'
  servicePrice.value = route.query.price || 0
  form.value.service = serviceId.value
  if (!serviceId.value) {
    alert('请先选择服务')
    router.push('/')
  }
  // 获取服务详情（含工作时段）
  try {
    const res = await request.get('/services/' + serviceId.value + '/')
    const svc = res?.data || res
    if (svc) {
      workStart.value = svc.work_start || ''
      workEnd.value = svc.work_end || ''
      svcDuration.value = svc.duration || 0
    }
  } catch (e) {}
})
</script>
