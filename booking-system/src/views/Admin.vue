<template>
  <div style="background:#f7f8fa;min-height:100vh;">
    <van-nav-bar title="管理后台" left-arrow @click-left="router.back()" />
    <van-loading v-if="loading" style="margin-top:80px;" />

    <template v-if="!loading">
      <!-- 自定义选项卡 -->
      <div style="display:flex;gap:0;margin-bottom:8px;background:#fff;border-radius:8px;overflow:hidden;">
        <div v-for="(t, i) in ['概览','分类管理','帖子审核']" :key="i"
          style="flex:1;text-align:center;padding:12px;cursor:pointer;font-size:14px;font-weight:600;transition:all 0.2s;"
          :style="adminTab === i ? 'color:#5c6bc0;border-bottom:3px solid #5c6bc0;background:#f8faff;' : 'color:#999;border-bottom:3px solid transparent;'"
          @click="adminTab = i">{{ t }}</div>
      </div>

      <!-- 概览 -->
      <div v-if="adminTab === 0">
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;padding:10px;">
          <div style="background:#fff;border-radius:8px;padding:15px;text-align:center;">
            <div style="font-size:24px;font-weight:bold;color:#5c6bc0;">{{ stats.total_users }}</div>
            <div style="font-size:12px;color:#969799;margin-top:4px;">用户总数</div>
          </div>
          <div style="background:#fff;border-radius:8px;padding:15px;text-align:center;">
            <div style="font-size:24px;font-weight:bold;color:#07c160;">{{ stats.total_providers }}</div>
            <div style="font-size:12px;color:#969799;margin-top:4px;">服务提供者</div>
          </div>
          <div style="background:#fff;border-radius:8px;padding:15px;text-align:center;">
            <div style="font-size:24px;font-weight:bold;color:#ee0a24;">{{ stats.total_services }}</div>
            <div style="font-size:12px;color:#969799;margin-top:4px;">服务总数</div>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:0 10px 10px;">
          <div style="background:#fff;border-radius:8px;padding:15px;text-align:center;">
            <div style="font-size:24px;font-weight:bold;color:#7232dd;">{{ stats.total_appointments }}</div>
            <div style="font-size:12px;color:#969799;margin-top:4px;">预约总数</div>
          </div>
          <div style="background:#fff;border-radius:8px;padding:15px;text-align:center;">
            <div style="font-size:24px;font-weight:bold;color:#f60;">{{ stats.total_reviews }}</div>
            <div style="font-size:12px;color:#969799;margin-top:4px;">评价总数</div>
          </div>
        </div>
        <div style="display:flex;gap:8px;padding:0 10px;margin-bottom:8px;">
          <van-field v-model="keyword" placeholder="搜索用户名..." clearable @keypress.enter="loadUsers" style="flex:1;" />
          <van-button type="primary" size="small" @click="loadUsers">搜索</van-button>
        </div>
        <van-cell-group inset style="margin:10px;">
          <van-cell v-for="u in users" :key="u.id">
            <template #title>
              <div style="display:flex;align-items:center;gap:10px;">
                <van-image round width="32" height="32" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + u.username + '&backgroundColor=5c6bc0&textColor=fff'" />
                <div>
                  <div style="font-size:14px;font-weight:500;">{{ u.username }}</div>
                  <div style="font-size:11px;color:#969799;">{{ u.role === 'provider' ? '服务提供者' : (u.role === 'admin' ? '管理员' : '用户') }}</div>
                </div>
              </div>
            </template>
            <template #value>
              <div style="font-size:11px;color:#969799;text-align:right;">
                <div>预约: {{ u.stats?.appointments || 0 }}</div>
                <div>服务: {{ u.stats?.services || 0 }}</div>
              </div>
            </template>
          </van-cell>
        </van-cell-group>
        <van-empty v-if="users.length === 0" description="暂无用户" />
      </div>

      <!-- 分类管理 -->
      <div v-if="adminTab === 1" style="margin:10px;">
        <h4 style="font-size:14px;margin:0 0 10px;color:#1a2332;">服务分类管理</h4>
        <div style="display:flex;gap:8px;margin-bottom:10px;">
          <van-field v-model="newCatName" placeholder="新分类名称" clearable style="flex:1;" />
          <van-button type="primary" size="small" :loading="addingCat" @click="addCategory">添加</van-button>
        </div>
        <div v-if="categories.length === 0" style="color:#999;font-size:13px;padding:10px 0;">暂无分类</div>
        <div v-for="c in categories" :key="c.name || c.id" style="display:flex;align-items:center;padding:8px 0;border-bottom:1px solid #f0f0f0;">
          <span style="flex:1;font-size:14px;">{{ c.name }}</span>
          <van-button size="mini" plain type="danger" @click="deleteCategory(c.id)">删除</van-button>
        </div>
      </div>

      <!-- 帖子审核 -->
      <div v-if="adminTab === 2" style="margin:10px;">
        <h4 style="font-size:14px;margin:0 0 10px;color:#1a2332;">帖子审核</h4>
        <van-loading v-if="pendingLoading" />
        <div v-if="pendingPosts.length === 0" style="color:#999;font-size:13px;padding:10px 0;">暂无待审核帖子</div>
        <div v-for="p in pendingPosts" :key="p.id" style="background:#fff;border-radius:12px;padding:14px;margin-bottom:8px;">
          <div style="font-size:12px;color:#5c6bc0;margin-bottom:4px;">{{ p.username }}</div>
          <div style="font-size:13px;line-height:1.5;color:#333;">{{ p.content }}</div>
          <div style="display:flex;gap:8px;margin-top:8px;">
            <van-button size="small" type="primary" round @click="approvePost(p.id)">通过</van-button>
            <van-button size="small" plain type="danger" round @click="rejectPost(p.id)">拒绝</van-button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../utils/request'

const router = useRouter()
const adminTab = ref(0)
const loading = ref(true)
const stats = ref({})
const users = ref([])
const keyword = ref('')

const loadData = async () => {
  try {
    const [statsRes, usersRes] = await Promise.all([
      request.get('/auth/admin/stats/'),
      request.get('/auth/admin/users/', { params: { search: keyword.value } }),
    ])
    stats.value = statsRes?.data || statsRes
    users.value = (usersRes?.data?.results || usersRes?.results || [])
  } catch (e) {
    alert('❌ ' + (e?.response?.data?.detail || '加载数据失败'))
    router.push('/')
  } finally {
    loading.value = false
  }
}

const loadUsers = () => {
  loading.value = true
  loadData()
}

// 分类管理
const categories = ref([])
const newCatName = ref('')
const addingCat = ref(false)

const loadCategories = async () => {
  try {
    const res = await request.get('/services/categories/')
    categories.value = res?.data || []
  } catch (e) {}
}

const addCategory = async () => {
  const name = newCatName.value.trim()
  if (!name) return
  addingCat.value = true
  try {
    await request.post('/services/categories/add/', { name })
    newCatName.value = ''
    await loadCategories()
  } catch (e) { alert(e?.response?.data?.message || '添加失败') }
  finally { addingCat.value = false }
}

const deleteCategory = async (id) => {
  try {
    await request.delete('/services/categories/' + id + '/delete/')
    await loadCategories()
  } catch (e) { alert(e?.response?.data?.message || '删除失败') }
}

// 帖子审核
const pendingPosts = ref([])
const pendingLoading = ref(false)

const loadPending = async () => {
  pendingLoading.value = true
  try {
    const res = await request.get('/posts/pending/')
    pendingPosts.value = res?.data || []
  } catch (e) {}
  finally { pendingLoading.value = false }
}

const approvePost = async (id) => {
  try {
    await request.post('/posts/' + id + '/approve/')
    await loadPending()
  } catch (e) { alert(e?.response?.data?.message || '操作失败') }
}

const rejectPost = async (id) => {
  try {
    await request.post('/posts/' + id + '/reject/')
    await loadPending()
  } catch (e) { alert('操作失败') }
}

onMounted(() => {
  loadData()
  loadCategories()
  loadPending()
})
</script>
