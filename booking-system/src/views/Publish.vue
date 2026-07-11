<template>
  <div style="padding:10px 0;background:#f7f8fa;min-height:100vh;">
    <van-tabs v-model:active="tabActive">
      <van-tab title="发布新服务">
        <van-form @submit="onSubmit" style="margin-top:10px;">
          <van-cell-group inset>
            <van-field v-model="form.name" label="服务名称" placeholder="请输入服务名称" :rules="[{ required: true, message: '请填写服务名称' }]" />
            <van-field label="服务分类" is-link readonly :model-value="form.category || '请选择分类'" :rules="[{ required: true, message: '请选择服务分类' }]" @click="showCatPicker = true" />
            <van-field v-model="form.price" label="价格(元)" placeholder="请输入价格" :rules="[{ required: true, message: '请填写价格' }]" />
            <van-field v-model="form.duration" label="服务时长(分钟)" placeholder="如：60" :rules="[{ required: true, message: '请填写时长' }]" />
            <van-field v-model="form.work_start" label="工作开始时间" type="time" placeholder="如：08:00" />
            <van-field v-model="form.work_end" label="工作结束时间" type="time" placeholder="如：18:00" />
            <van-field v-model="form.address" label="服务地址" placeholder="请输入地址" :rules="[{ required: true, message: '请填写地址' }]" />
            <van-field v-model="form.city" label="城市" placeholder="如：武汉" />
            <van-uploader v-model="svcFiles" :max-count="1" :deletable="false" style="padding:10px 16px;" />
          <span v-if="form.image_url" style="font-size:12px;color:#07c160;margin-left:8px;">✅ 已选择</span>
            <van-field v-model="form.description" label="服务描述" type="textarea" rows="4" placeholder="请详细描述服务内容" :rules="[{ required: true, message: '请填写描述' }]" />
          </van-cell-group>
          <van-popup v-model:show="showCatPicker" position="bottom" round>
            <div style="padding:16px 20px 30px;max-height:55vh;overflow-y:auto;">
              <h3 style="text-align:center;margin:0 0 12px;">选择分类</h3>
              <div style="display:flex;align-items:center;background:#f5f5f5;border-radius:8px;padding:0 10px;margin-bottom:10px;">
                <svg viewBox="0 0 24 24" width="16" height="16" fill="#999"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input v-model="catSearch" placeholder="搜索分类..." style="flex:1;border:none;outline:none;background:transparent;padding:10px 8px;font-size:14px;color:#333;" />
                <van-icon v-if="catSearch" name="clear" size="16" color="#bbb" @click="catSearch=''" />
              </div>
              <div v-for="c in resultCats" :key="c.id || c.name" style="padding:12px 16px;font-size:14px;border-bottom:1px solid #f5f5f5;cursor:pointer;" @click="pickCategory(c)">{{ c.name }}</div>
              <div v-if="resultCats.length === 0" style="text-align:center;color:#999;padding:20px 0;">无匹配分类</div>
              <van-button plain block style="margin-top:12px;" @click="showCatPicker = false">取消</van-button>
            </div>
          </van-popup>
          <div style="margin:16px;">
            <van-button round block type="primary" native-type="submit" :loading="submitting">立即发布</van-button>
          </div>
        </van-form>
      </van-tab>

      <van-tab title="我的服务">
        <van-empty v-if="myServices.length === 0" description="暂无已发布的服务" />
        <van-swipe-cell v-for="s in myServices" :key="s.id">
          <van-card
            :title="s.name"
            :desc="s.category + ' | ' + s.duration + '分钟'"
            :price="'¥' + s.price"
            :num="'评分: ' + s.rating"
            @click="router.push('/service/' + s.id)"
          />
          <template #right>
            <van-button square type="danger" text="删除" style="height:100%;" @click="onDelete(s.id)" />
          </template>
        </van-swipe-cell>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { serviceApi } from '../api'
import request from '../utils/request'
import { extractList } from '../utils/data'

const router = useRouter()
const tabActive = ref(0)
const submitting = ref(false)
const myServices = ref([])
const categories = ref([])
const showCatPicker = ref(false)
const catSearch = ref('')

const resultCats = computed(() => {
  if (!catSearch.value) return categories.value
  const q = catSearch.value.toLowerCase()
  return categories.value.filter(c => (c.name || '').toLowerCase().includes(q))
})

const loadCategories = async () => {
  try {
    const res = await request.get('/services/categories/')
    categories.value = res?.data || []
  } catch (e) {}
}

const pickCategory = (c) => {
  form.value.category = c.name
  showCatPicker.value = false
}

const form = ref({
  name: '',
  category: '',
  price: '',
  duration: '',
  address: '',
  city: '武汉',
  image_url: '',
  work_start: '',
  work_end: '',
  description: '',
})

const loadMyServices = async () => {
  try {
    const res = await serviceApi.getMyServices()
    myServices.value = extractList(res)
  } catch (e) {
    console.error('加载服务列表失败', e)
  }
}

const onSubmit = async () => {
  submitting.value = true
  try {
    await serviceApi.publish({
      name: form.value.name,
      category: form.value.category,
      price: form.value.price,
      duration: parseInt(form.value.duration),
      address: form.value.address,
      city: form.value.city,
      description: form.value.description,
      image_url: form.value.image_url,
    })
    alert('服务发布成功！')
    form.value = { name: '', category: '', price: '', duration: '', address: '', city: '武汉',
  image_url: '', description: '' }
    await loadMyServices()
    tabActive.value = 1
  } catch (e) {
    const d = e?.response?.data
    let msg = '发布失败'
    if (!d) {
      msg = '无法连接到服务器'
    } else if (d?.message) {
      msg = d.message
    } else if (d?.detail) {
      msg = d.detail
    } else if (typeof d === 'object' && !Array.isArray(d)) {
      // DRF 默认错误格式: {"field_name": ["error msg"]}
      const keys = Object.keys(d)
      if (keys.length > 0) {
        const firstErr = d[keys[0]]
        msg = firstErr
        if (Array.isArray(firstErr) && firstErr.length > 0) {
          msg = firstErr[0]
        }
      }
    } else if (e?.message) {
      msg = e.message
    }
    alert('❌ ' + msg)
  } finally {
    submitting.value = false
  }
}

const onDelete = async (id) => {
  try {
    await serviceApi.delete(id)
    alert('删除成功')
    await loadMyServices()
  } catch (e) {
    alert('删除失败')
  }
}

const svcFiles = ref([])
const stopSvcWatch = watch(svcFiles, (val) => {
  if (val.length > 0 && val[0]?.file) {
    const reader = new FileReader()
    reader.readAsDataURL(val[0].file)
    reader.onload = () => { form.value.image_url = reader.result }
  }
})

onMounted(() => { loadMyServices(); loadCategories() })
</script>
