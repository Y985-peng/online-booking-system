<template>
  <div class="home">
    <van-search
      v-model="searchText"
      placeholder="搜索服务名称、描述、地址..."
      @search="onSearch"
      @clear="onClear"
    />

    <!-- 搜索结果 -->
    <template v-if="searchText">
      <van-loading v-if="searching" style="margin-top:50px;" />
      <van-empty v-else-if="searchResults.length === 0" description="未找到相关服务" />
      <van-card v-for="s in searchResults" :key="s.id"
        :title="s.name"
        :desc="s.category + ' | ' + (s.duration || '') + '分钟'"
        :price="'¥' + (s.price || 0)"
        :num="'评分 ' + (s.rating || 0)"
        :thumb="'https://api.dicebear.com/7.x/initials/svg?seed=' + (s.name || s.id) + '&backgroundColor=1989fa&textColor=fff'"
        @click="goDetail(s.id)"
      />
    </template>

    <!-- 全部服务 -->
    <template v-else>
      <van-loading v-if="loading" style="margin-top:50px;" />
      <div style="padding:0 15px;" v-if="!loading">
        <h3 class="section-title">全部服务</h3>
        <van-card v-for="service in hotServices" :key="service.id"
          :title="service.name"
          :desc="service.category + ' | ' + (service.duration || '') + '分钟'"
          :price="'¥' + (service.price || 0)"
          :num="'评分 ' + (service.rating || 0)"
          :thumb="'https://api.dicebear.com/7.x/initials/svg?seed=' + (service.name || service.id) + '&backgroundColor=1989fa&textColor=fff'"
          @click="goDetail(service.id)"
        />
        <van-empty v-if="hotServices.length === 0" description="暂无服务" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { serviceApi } from '../api'
import { extractList } from '../utils/data'

const router = useRouter()
const searchText = ref('')
const hotServices = ref([])
const loading = ref(true)
const searchResults = ref([])
const searching = ref(false)

const loadHotServices = async () => {
  try {
    const res = await serviceApi.getList({ ordering: '-rating' })
    hotServices.value = extractList(res)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const onSearch = async (val) => {
  const kw = (val || searchText.value || '').trim()
  if (!kw) return
  searchText.value = kw
  searching.value = true
  try {
    const res = await serviceApi.getList({ search: kw })
    searchResults.value = extractList(res)
    const lower = kw.toLowerCase()
    searchResults.value.sort((a, b) => {
      const an = (a.name || '').toLowerCase(), bn = (b.name || '').toLowerCase()
      if (an === lower) return -1; if (bn === lower) return 1
      if (an.startsWith(lower)) return -1; if (bn.startsWith(lower)) return 1
      return 0
    })
  } catch (e) { console.error(e) }
  searching.value = false
}

const onClear = () => {
  searchText.value = ''
  searchResults.value = []
}

const goDetail = (id) => router.push(`/service/${id}`)

onMounted(loadHotServices)
</script>

<style scoped>
.home { padding-bottom: 20px; background: #f7f8fa; }
</style>
