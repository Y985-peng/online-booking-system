<template>
  <div style="background:#f7f8fa;min-height:100vh;">
    <van-nav-bar title="消息" left-arrow @click-left="router.back()" />

    <van-tabs v-model:active="activeTab">
      <!-- ===== 消息 tab ===== -->
      <van-tab title="消息" name="messages">
        <van-loading v-if="loading" style="margin-top:80px;" />
        <template v-if="!loading">
          <van-empty v-if="conversations.length === 0" description="暂无对话" />
          <van-cell-group inset style="margin:10px;">
            <van-cell v-for="c in conversations" :key="c.id" is-link @click="openChat(c)">
              <template #title>
                <div style="font-weight:bold;display:flex;align-items:center;gap:8px;">
                  {{ getConvName(c) }}
                  <van-badge v-if="c.unread_count > 0" :content="c.unread_count" />
                </div>
                <div v-if="c.last_message" style="font-size:12px;color:#969799;margin-top:4px;">
                  {{ c.last_message.sender }}: {{ c.last_message.content }}
                </div>
              </template>
              <template #label>
                <div style="font-size:11px;color:#c8c9cc;">{{ c.participant_names?.join('、') }}</div>
              </template>
              <template #value>
                <span v-if="c.last_message" style="font-size:11px;color:#969799;">{{ c.last_message.time }}</span>
              </template>
            </van-cell>
          </van-cell-group>
        </template>
      </van-tab>

      <!-- ===== 通知 tab ===== -->
      <van-tab title="通知" name="notifications">
        <van-loading v-if="notifLoading" style="margin-top:80px;" />
        <template v-if="!notifLoading">
          <div v-if="notifications.length > 0" style="text-align:right;padding:8px 16px;">
            <van-button size="mini" plain @click="markAllRead">全部已读</van-button>
          </div>
          <van-empty v-if="notifications.length === 0" description="暂无通知" />
          <van-cell-group inset style="margin:10px;">
            <van-cell v-for="n in notifications" :key="n.id" is-link @click="goToPost(n)">
              <template #title>
                <div style="display:flex;align-items:center;gap:8px;">
                  <span v-if="n.type === 'like'" style="color:#ee0a24;">❤️</span>
                  <span v-else-if="n.type === 'favorite'" style="color:#ffa726;">⭐</span>
                  <span v-else style="color:#5c6bc0;">💬</span>
                  <div>
                    <div style="font-size:13px;">
                      <strong>{{ n.from_username }}</strong>
                      {{ n.type === 'like' ? '赞了你的帖子' : n.type === 'favorite' ? '收藏了你的帖子' : '评论了你的帖子' }}
                    </div>
                    <div style="font-size:11px;color:#969799;margin-top:2px;">{{ n.post_content }}</div>
                  </div>
                </div>
              </template>
              <template #value>
                <span style="font-size:10px;color:#bbb;white-space:nowrap;">{{ formatTime(n.created_at) }}</span>
              </template>
            </van-cell>
          </van-cell-group>
        </template>
      </van-tab>
    </van-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import request from '../utils/request'

const router = useRouter()
const userStore = useUserStore()
const myName = ref(userStore.userInfo?.username || '')

const activeTab = ref('messages')
const loading = ref(true)
const conversations = ref([])
const notifLoading = ref(false)
const notifications = ref([])
let timer = null
let notifTimer = null

const getConvName = (conv) => {
  const others = (conv.participant_names || []).filter(n => n !== myName.value)
  return others[0] || conv.service_name || '聊天'
}

/* ---- 对话 ---- */
const loadConvs = async () => {
  try {
    const res = await request.get('/chat/conversations/')
    conversations.value = res?.data || []
  } catch (e) {
    console.error('加载对话失败', e)
  } finally { loading.value = false }
}

const openChat = (c) => {
  router.push(`/chat/${c.id}?name=${encodeURIComponent(getConvName(c))}`)
}

/* ---- 通知 ---- */
const loadNotifs = async () => {
  notifLoading.value = true
  try {
    const res = await request.get('/posts/notifications/')
    notifications.value = res?.data || []
  } catch (e) { notifications.value = [] }
  finally { notifLoading.value = false }
}

const markAllRead = async () => {
  try {
    await request.post('/posts/notifications/read-all/')
    notifications.value.forEach(n => n.is_read = true)
  } catch (e) {}
}

const goToPost = (n) => {
  if (n.post_id) router.push('/post/' + n.post_id)
}

const formatTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadConvs()
  loadNotifs()
  timer = setInterval(loadConvs, 5000)
  notifTimer = setInterval(loadNotifs, 15000)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (notifTimer) clearInterval(notifTimer)
})
</script>
