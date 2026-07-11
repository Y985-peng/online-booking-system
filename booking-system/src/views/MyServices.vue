<template>
  <div style="background:#f7f8fa;min-height:100vh;">
    <div style="display:flex;align-items:center;padding:10px 12px;background:#fff;border-bottom:1px solid #efefef;">
      <button style="background:none;border:none;font-size:26px;color:#333;cursor:pointer;padding:0;line-height:1;margin-right:8px;" @click="router.back()">‹</button>
      <div style="flex:1;font-size:16px;font-weight:600;color:#111;">我的服务</div>
      <button style="background:none;border:none;display:flex;align-items:center;gap:4px;cursor:pointer;color:#5c6bc0;font-size:14px;padding:6px 10px;border-radius:6px;" @click="goPublish">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="#5c6bc0"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        <span>发布服务</span>
      </button>
    </div>

    <van-loading v-if="loading" style="margin-top:80px;" />

    <template v-if="!loading">
      <div v-if="services.length === 0" style="text-align:center;color:#b0bcd6;padding:60px 0;font-size:14px;">
        暂无服务
        <div style="margin-top:16px;">
          <van-button type="primary" size="small" round @click="goPublish">发布服务</van-button>
        </div>
      </div>

      <div v-for="s in services" :key="s.id" style="background:#f8faff;border-radius:14px;padding:14px 16px;margin:8px 12px;">
        <div style="display:flex;align-items:center;gap:12px;">
          <van-image v-if="s.image_url" round width="48" height="48" :src="s.image_url" fit="cover" />
          <div v-else style="width:48px;height:48px;border-radius:12px;background:#5c6bc0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:600;flex-shrink:0;">
            {{ s.name?.charAt(0) || '?' }}
          </div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:15px;font-weight:600;color:#1a2332;">{{ s.name }}</div>
            <div style="font-size:12px;color:#8c9db5;margin-top:2px;">{{ s.category }} · ¥{{ s.price }} / {{ s.duration }}分钟</div>
            <div v-if="s.address" style="font-size:11px;color:#b0bcd6;margin-top:2px;">📍 {{ s.address }}</div>
          </div>
          <van-button size="small" type="primary" round @click="openEdit(s)" style="white-space:nowrap;">编辑</van-button>
        </div>
      </div>
    </template>

    <!-- 编辑弹窗 -->
    <van-popup v-model:show="showEdit" position="center" round :style="{ width: '88%' }">
      <div style="padding:24px 20px 20px;max-height:80vh;overflow-y:auto;">
        <h3 style="text-align:center;margin:0 0 18px;font-size:16px;">编辑服务</h3>
        <van-field v-model="form.name" label="名称" placeholder="服务名称" clearable />
        <van-field v-model="form.category" label="分类" placeholder="选择分类" is-link readonly @click="showCategoryPicker = true" />
        <van-field v-model="form.price" label="价格" type="number" placeholder="价格" clearable />
        <van-field v-model="form.duration" label="时长(分钟)" type="number" placeholder="时长" clearable />
        <van-field v-model="form.work_start" label="工作开始时间" type="time" placeholder="如：08:00" clearable />
        <van-field v-model="form.work_end" label="工作结束时间" type="time" placeholder="如：18:00" clearable />
        <van-field v-model="form.address" label="地址" placeholder="地址" clearable />
        <van-field v-model="form.description" type="textarea" rows="3" label="介绍" placeholder="服务介绍" />
        <!-- 分类选择器 -->
        <van-popup v-model:show="showCategoryPicker" position="bottom" round>
          <div style="padding:16px 20px 30px;max-height:55vh;overflow-y:auto;">
            <h4 style="margin:0 0 12px;text-align:center;">选择分类</h4>
            <div style="display:flex;align-items:center;background:#f5f5f5;border-radius:8px;padding:0 10px;margin-bottom:10px;">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="#999"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
              <input v-model="catSearch" placeholder="搜索分类..." style="flex:1;border:none;outline:none;background:transparent;padding:10px 8px;font-size:14px;color:#333;" />
              <van-icon v-if="catSearch" name="clear" size="16" color="#bbb" @click="catSearch=''" />
            </div>
            <div v-for="c in filteredCategories" :key="c.id || c.name" 
                 style="padding:12px 16px;font-size:14px;border-bottom:1px solid #f5f5f5;cursor:pointer;color:#5c6bc0;"
                 @click="selectCategory(c.name)">{{ c.name }}</div>
            <div v-if="filteredCategories.length === 0" style="text-align:center;color:#999;padding:20px 0;">无匹配分类</div>
            <van-button plain block style="margin-top:12px;" @click="showCategoryPicker = false">取消</van-button>
          </div>
        </van-popup>
        <div style="margin-top:18px;display:flex;gap:10px;">
          <van-button plain style="flex:1;" @click="showEdit = false">取消</van-button>
          <van-button type="primary" style="flex:1;" :loading="saving" @click="saveEdit">保存</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { extractList } from '../utils/data'

const router = useRouter()
const loading = ref(true)
const services = ref([])
const showEdit = ref(false)
const showCategoryPicker = ref(false)
const categories = ref([])
const catSearch = ref('')

const filteredCategories = computed(() => {
  if (!catSearch.value) return categories.value
  const q = catSearch.value.toLowerCase()
  return categories.value.filter(c => (c.name || '').toLowerCase().includes(q))
})
const saving = ref(false)
const editingId = ref(null)
const form = ref({
  name: '', category: '', price: '', duration: '', work_start: '', work_end: '', address: '', description: ''
})

const loadCategories = async () => {
  try {
    const res = await request.get('/services/categories/')
    categories.value = res?.data || res || []
  } catch (e) { categories.value = [] }
}

const selectCategory = (name) => {
  form.value.category = name
  showCategoryPicker.value = false
}

const loadServices = async () => {
  try {
    const res = await request.get('/services/my/')
    services.value = extractList(res)
  } catch (e) { services.value = [] }
  finally { loading.value = false }
}

const goPublish = () => { router.push('/publish') }

const openEdit = (s) => {
  editingId.value = s.id
  form.value = {
    name: s.name || '',
    category: s.category || '',
    price: s.price || '',
    duration: s.duration || '',
    work_start: s.work_start || '',
    work_end: s.work_end || '',
    address: s.address || '',
    description: s.description || '',
  }
  showEdit.value = true
}

const saveEdit = async () => {
  saving.value = true
  try {
    await request.put('/services/' + editingId.value + '/update/', form.value)
    showEdit.value = false
    await loadServices()
  } catch (e) { alert('更新失败') }
  finally { saving.value = false }
}

onMounted(() => { loadServices(); loadCategories() })
</script>
