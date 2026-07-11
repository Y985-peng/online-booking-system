<template>
  <div class="categories-page">
    <!-- PC 端：双栏布局 -->
    <div class="cat-layout">
      <!-- 左侧分类列表 -->
      <aside v-show="showCats" class="cat-sidebar">
        <div class="cat-title">全部分类</div>
        <div v-for="cat in categories" :key="cat.name"
          class="cat-item"
          :class="{ active: selected === cat.name }"
          @click="selectCategory(cat)">
          <span class="cat-name">{{ cat.name }}</span>
        </div>
      </aside>

      <!-- 右侧服务列表 -->
      <div class="cat-content">
        <div class="cat-header">
          <button v-if="!showCats" class="cat-back-btn" @click="showCats = true">‹ 全部分类</button>
          <h3>{{ selected || '选择分类' }}</h3>
          <span class="cat-count">{{ services.length }} 个服务</span>
        </div>

        <van-loading v-if="loading" style="margin-top:40px;" />

        <template v-if="!loading">
          <van-empty v-if="services.length === 0" description="该分类暂无服务" />
          <van-card
            v-for="s in services" :key="s.id"
            :title="s.name"
            :desc="s.provider_name + ' | ' + (s.duration || '弹性') + '分钟'"
            :price="'¥' + (s.price || 0)"
            :thumb="'https://api.dicebear.com/7.x/initials/svg?seed=' + (s.name || s.id) + '&backgroundColor=1989fa&textColor=fff'"
            @click="goDetail(s.id)"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'
import { serviceApi } from '../api'
import { extractList } from '../utils/data'

const router = useRouter()
const selected = ref('医疗')
const services = ref([])
const loading = ref(false)
const showCats = ref(true)

const categories = ref([])

const loadCategories = async () => {
  const defaults = ['医疗', '美容', '健身', '家教', '家政', '维修', '摄影', '设计', '法律', '翻译', '编程', '金融', '教育', '餐饮', '娱乐']
  try {
    const res = await request.get('/services/categories/')
    const apiCats = res?.data || []
    const seen = new Set()
    const merged = []
    for (const c of apiCats) {
      const name = c.name?.trim()
      if (name && !seen.has(name.toLowerCase())) {
        seen.add(name.toLowerCase())
        merged.push({ name })
      }
    }
    for (const name of defaults) {
      if (!seen.has(name.toLowerCase())) {
        seen.add(name.toLowerCase())
        merged.push({ name })
      }
    }
    categories.value = merged
  } catch (e) {
    categories.value = defaults.map(n => ({ name: n }))
  }
}


const selectCategory = (cat) => {
  selected.value = cat.name
  showCats.value = false
  loadServices()
}

const loadServices = async () => {
  loading.value = true
  try {
    const res = await serviceApi.getList({ category: selected.value })
    services.value = extractList(res)
  } catch (e) {
    console.error('加载服务失败', e)
  } finally {
    loading.value = false
  }
}

const goDetail = (id) => router.push(`/service/${id}`)

onMounted(() => { loadServices(); loadCategories() })
</script>

<style scoped>
.categories-page { min-height: 100vh; background: #f5f6fa; }

.cat-layout {
  display: flex;
  gap: 0;
  max-width: 1200px;
  margin: 0 auto;
}

.cat-sidebar {
  width: 160px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #f0f0f0;
  padding: 12px 0;
}

.cat-title {
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
}

.cat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.15s;
}
.cat-name { font-size: 14px; }
.cat-item:hover { background: #f5f7fa; color: #5c6bc0; }
.cat-item.active { background: #ecf5ff; color: #5c6bc0; font-weight: 600; border-right: 3px solid #5c6bc0; }

.cat-content {
  flex: 1;
  padding: 16px;
}

.cat-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 16px;
}
.cat-header h3 { margin: 0; font-size: 20px; color: #333; }
.cat-count { font-size: 13px; color: #999; }

/* 移动端 */
@media (max-width: 767px) {
  .cat-layout { flex-direction: column; }
  .cat-sidebar {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    padding: 8px;
    gap: 6px;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
  }
  .cat-title { display: none; }
  .cat-item {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    border: 1px solid #eee;
  }
  .cat-item.active { border-color: #5c6bc0; border-right: 3px solid #5c6bc0; }
  .cat-content { padding: 12px; }
}
</style>
