<template>
  <div class="desktop-layout">
    <aside class="sidebar">
      <div class="logo">预约系统</div>
      <nav>
        <div
          v-for="item in navItems"
          :key="item.path"
          class="nav-item"
          :class="{ active: currentPath.startsWith(item.path) }"
          @click="goTo(item.path)"
        >
          <van-icon :name="item.icon" />
          <span>{{ item.label }}</span>
          <span v-if="item.isChat && unreadCount > 0" class="unread-dot">{{ unreadCount }}</span>
        </div>
      </nav>
      <div class="sidebar-user" @click="goTo('/profile')">
        <van-image round width="32" height="32" :src="avatarUrl" />
        <span>{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}</span>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const currentPath = computed(() => route.path)
const unreadCount = ref(0)
let unreadTimer = null

const fetchUnread = async () => {
  if (!userStore.token) { unreadCount.value = 0; return }
  try {
    const chatRes = await request.get('/chat/unread-count/')
    const chatCount = chatRes?.data?.count || 0
    let notifCount = 0
    try {
      const nRes = await request.get('/posts/notifications/unread-count/')
      notifCount = nRes?.data?.count || 0
    } catch (e) {}
    unreadCount.value = chatCount + notifCount
  } catch (e) {}
}

onMounted(() => {
  fetchUnread()
  unreadTimer = setInterval(fetchUnread, 10000)
})

onUnmounted(() => { if (unreadTimer) clearInterval(unreadTimer) })

const avatarUrl = computed(() => {
  const u = userStore.userInfo?.username || '?'
  return userStore.userInfo?.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${u}&backgroundColor=5c6bc0&textColor=fff`
})

const navItems = [
  { path: '/', icon: 'home-o', label: '首页', isChat: false },
  { path: '/categories', icon: 'apps-o', label: '分类', isChat: false },
  { path: '/posts', icon: 'fire-o', label: '动态', isChat: false },
  { path: '/chat', icon: 'chat-o', label: '消息', isChat: true },
  { path: '/orders', icon: 'orders-o', label: '订单', isChat: false },
  { path: '/profile', icon: 'user-o', label: '个人', isChat: false },
]

const goTo = (path) => { router.push(path) }
</script>

<style scoped>
.desktop-layout {
  display: flex; height: 100vh;
}

.sidebar {
  width: 220px; background: #1a1a2e; color: #ccc;
  display: flex; flex-direction: column; flex-shrink: 0;
}

.logo {
  padding: 20px; font-size: 18px; font-weight: bold; color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

nav { flex: 1; padding: 8px 0; overflow-y: auto; }

.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px; cursor: pointer; font-size: 14px;
  transition: all 0.15s;
  position: relative;
}
.nav-item:hover { background: rgba(255,255,255,0.06); color: #fff; }
.nav-item.active { background: #5c6bc0; color: #fff; }

.unread-dot {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  background: #ee0a24;
  color: #fff;
  font-size: 11px;
  font-weight: bold;
  border-radius: 9px;
  padding: 0 5px;
}

.sidebar-user {
  display: flex; align-items: center; gap: 10px;
  padding: 16px 20px; cursor: pointer; font-size: 14px; color: #fff;
  border-top: 1px solid rgba(255,255,255,0.08);
}
.sidebar-user:hover { background: rgba(255,255,255,0.06); }

.main-content {
  flex: 1; overflow-y: auto;
  background: #f5f6fa;
}

.main-content :deep(.van-tabbar) { display: none !important; }
.main-content :deep(.van-nav-bar) { display: none; }
</style>
