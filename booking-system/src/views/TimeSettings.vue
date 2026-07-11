<template>
  <div style="padding:15px;background:#f7f8fa;min-height:100vh;">
    <h2 style="margin:0 0 15px;">时段设置</h2>

    <van-form @submit="onAdd">
      <van-cell-group inset>
        <van-field label="星期" is-link readonly :model-value="selectedDayLabel" @click="showDayPicker = true" />
        <van-field label="开始时间" is-link readonly :model-value="form.start_time" @click="showStartPicker = true" />
        <van-field label="结束时间" is-link readonly :model-value="form.end_time" @click="showEndPicker = true" />
      </van-cell-group>
      <div style="margin:10px 16px;">
        <van-button round block type="primary" native-type="submit" :loading="adding">添加可用时段</van-button>
      </div>
    </van-form>

    <van-divider />

    <h3 style="margin:0 0 10px;">当前可用时段</h3>
    <van-empty v-if="timeSlots.length === 0" description="暂未设置可用时段" />
    <van-swipe-cell v-for="slot in timeSlots" :key="slot.id">
      <van-cell :title="slot.day_name" :label="slot.start_time + ' - ' + slot.end_time" />
      <template #right>
        <van-button square type="danger" text="删除" style="height:100%;" @click="onDelete(slot.id)" />
      </template>
    </van-swipe-cell>

    <van-action-sheet v-model:show="showDayPicker" title="选择星期">
      <van-radio-group v-model="form.day_of_week">
        <van-cell-group>
          <van-cell v-for="d in dayOptions" :key="d.value" :title="d.label" clickable @click="selectDay(d)">
            <template #right-icon>
              <van-radio :name="d.value" />
            </template>
          </van-cell>
        </van-cell-group>
      </van-radio-group>
    </van-action-sheet>

    <van-popup v-model:show="showStartPicker" position="bottom">
      <van-time-picker :min-hour="0" :max-hour="23" @confirm="onStartConfirm" @cancel="showStartPicker = false" />
    </van-popup>
    <van-popup v-model:show="showEndPicker" position="bottom">
      <van-time-picker :min-hour="0" :max-hour="23" @confirm="onEndConfirm" @cancel="showEndPicker = false" />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { extractList } from '../utils/data'
import { timeSlotApi } from '../api'

const timeSlots = ref([])
const adding = ref(false)
const showDayPicker = ref(false)
const showStartPicker = ref(false)
const showEndPicker = ref(false)
const selectedDayLabel = ref('请选择')

const form = ref({ day_of_week: '', start_time: '09:00', end_time: '18:00' })

const dayOptions = [
  { value: 'monday', label: '周一' },
  { value: 'tuesday', label: '周二' },
  { value: 'wednesday', label: '周三' },
  { value: 'thursday', label: '周四' },
  { value: 'friday', label: '周五' },
  { value: 'saturday', label: '周六' },
  { value: 'sunday', label: '周日' },
]

const selectDay = (d) => {
  form.value.day_of_week = d.value
  selectedDayLabel.value = d.label
  showDayPicker.value = false
}

const onStartConfirm = ({ selectedValues }) => {
  form.value.start_time = selectedValues[0] + ':' + selectedValues[1]
  showStartPicker.value = false
}
const onEndConfirm = ({ selectedValues }) => {
  form.value.end_time = selectedValues[0] + ':' + selectedValues[1]
  showEndPicker.value = false
}

const loadSlots = async () => {
  try {
    const res = await timeSlotApi.getList()
    timeSlots.value = extractList(res)
  } catch (e) {
    console.error('加载时段失败', e)
  }
}

const onAdd = async () => {
  if (!form.value.day_of_week) { alert('请选择星期'); return }
  adding.value = true
  try {
    await timeSlotApi.create({
      day_of_week: form.value.day_of_week,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
    })
    alert('时段添加成功')
    form.value = { day_of_week: '', start_time: '09:00', end_time: '18:00' }
    selectedDayLabel.value = '请选择'
    await loadSlots()
  } catch (e) {
    const d = e?.response?.data
    let msg = '添加失败'
    if (d?.message) {
      msg = d.message
    } else if (d?.detail) {
      msg = d.detail
    } else if (typeof d === 'object' && !Array.isArray(d)) {
      const keys = Object.keys(d)
      if (keys.length > 0) {
        const firstErr = d[keys[0]]
        msg = Array.isArray(firstErr) ? firstErr[0] : String(firstErr)
      }
    } else if (e?.message) {
      msg = e.message
    }
    alert('❌ ' + msg)
  } finally {
    adding.value = false
  }
}

const onDelete = async (id) => {
  try {
    await timeSlotApi.delete(id)
    await loadSlots()
  } catch (e) {
    const d = e?.response?.data
    let msg = '删除失败'
    if (d?.message) msg = d.message
    else if (d?.detail) msg = d.detail
    else if (typeof d === 'object' && !Array.isArray(d)) {
      const keys = Object.keys(d)
      if (keys.length > 0) msg = Array.isArray(d[keys[0]]) ? d[keys[0]][0] : String(d[keys[0]])
    }
    else if (e?.message) msg = e.message
    alert('❌ ' + msg)
  }
}

onMounted(loadSlots)
</script>
