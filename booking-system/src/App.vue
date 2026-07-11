<template>
  <div class="app-container">
    <!-- 桌面端布局 -->
    <DesktopLayout v-if="isDesktop && $route.path !== '/login'" />
    
    <!-- 移动端布局 -->
    <template v-if="!isDesktop && $route.path !== '/login'">
      <router-view />
      <van-tabbar v-model="activeTab" @change="onTabChange" :active-color="'#5c6bc0'">
        <van-tabbar-item icon="home-o" name="home">首页</van-tabbar-item>
        <van-tabbar-item icon="apps-o" name="categories">分类</van-tabbar-item>
        <van-tabbar-item icon="fire-o" name="posts">动态</van-tabbar-item>
        <van-tabbar-item icon="chat-o" name="chat" :badge="unreadCount || undefined">消息</van-tabbar-item>
        <van-tabbar-item icon="orders-o" name="orders">订单</van-tabbar-item>
        <van-tabbar-item icon="user-o" name="profile">个人</van-tabbar-item>
      </van-tabbar>
    </template>

    <!-- 登录页 -->
    <router-view v-if="$route.path === '/login'" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResponsive } from './composables/useResponsive'
import DesktopLayout from './views/DesktopLayout.vue'
import request from './utils/request'

const { isDesktop } = useResponsive()
const route = useRoute()
const router = useRouter()

const unreadCount = ref(0)
let unreadTimer = null

const fetchUnread = async () => {
  if (!localStorage.getItem('token')) { unreadCount.value = 0; return }
  if (document.hidden) return  // don't poll when tab is hidden
  try {
    await Promise.all([
      request.get('/chat/unread-count/').then(r => r?.data?.count || 0).catch(() => 0),
      request.get('/posts/notifications/unread-count/').then(r => r?.data?.count || 0).catch(() => 0),
    ]).then(([chatCount, notifCount]) => {
      unreadCount.value = chatCount + notifCount
    })
  } catch (e) { /* ignore polling errors */ }
}

onMounted(() => {
  fetchUnread()
  unreadTimer = setInterval(fetchUnread, 15000)  // poll every 15s instead of 10s
})

// Listen for visibility changes to prevent flooding inactive tab
document.addEventListener('visibilitychange', () => {
  if (!document.hidden && localStorage.getItem('token')) fetchUnread()
})

onUnmounted(() => { if (unreadTimer) clearInterval(unreadTimer) })

const activeTab = ref('home')

const routeNameMap = {
  'Home': 'home', 'PostList': 'posts',
  'Categories': 'categories',
  'Chat': 'chat', 'ChatConversation': 'chat',
  'Orders': 'orders', 'Profile': 'profile'
}

watch(() => route.name, (newName) => {
  if (newName && routeNameMap[newName]) activeTab.value = routeNameMap[newName]
}, { immediate: true })

const onTabChange = (name) => {
  const routeMap = {
    'home': '/', 'posts': '/posts',
    'categories': '/categories',
    'chat': '/chat', 'orders': '/orders', 'profile': '/profile'
  }
  if (routeMap[name]) router.push(routeMap[name])
}
</script>

<style>
/* 全局样式已经写在 global.css 和 responsive.css 里 */
</style>
