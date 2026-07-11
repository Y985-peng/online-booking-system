<template>
  <div class="wc-chat">
    <!-- ===== 顶部栏 ===== -->
    <div class="wc-header">
      <div class="wc-header-left">
        <button class="wc-back" @click="router.back()">‹</button>
      </div>
      <div class="wc-header-mid">
        <p class="wc-header-title">{{ convName }}</p>
      </div>
      <div class="wc-header-right"></div>
    </div>

    <!-- ===== 消息区 ===== -->
    <van-loading v-if="loading" style="margin-top:80px;" />
    <div v-else ref="msgListRef" class="wc-body">
      <van-empty v-if="messages.length === 0" description="暂无消息" style="padding-top:60px;" />

      <template v-for="(m, idx) in messages" :key="m.id">
        <!-- 时间分隔线 -->
        <div v-if="showTimeGap(m, idx)" class="wc-time">
          <p>{{ formatTimeSep(m.created_at) }}</p>
        </div>

        <!-- ================================================================
             对方消息：头像 → [名字 + 气泡] → 时间   靠左
             ================================================================ -->
        <div v-if="!isMe(m)" class="msg-row them">
          <div class="them-avatar-box">
            <div class="them-avatar" :style="{ background: avatarColor(m.sender_name) }">
              <p>{{ m.sender_name?.charAt(0) || '?' }}</p>
            </div>
          </div>
          <div class="them-msg-col">
            <p class="bubble-name">{{ m.sender_name }}</p>
            <div class="them-bubble"><p>{{ m.content }}</p></div>
          </div>
          <span class="msg-time">{{ formatTime(m.created_at) }}</span>
        </div>

        <!-- ================================================================
             自己消息：时间 → [名字 + 气泡] → 头像 → 已读   靠右
             ================================================================ -->
        <div v-else class="msg-row me">
          <span class="msg-time">{{ formatTime(m.created_at) }}</span>
          <div class="me-msg-col">
            <p class="bubble-name">我</p>
            <div class="me-bubble"><p>{{ m.content }}</p></div>
          </div>
          <div class="me-avatar-box">
            <div class="me-avatar">
              <img v-if="myAvatar" class="avatar-img" :src="myAvatar" alt="" />
              <p v-else>我</p>
            </div>
          </div>
          <span v-if="m.is_read" class="msg-read">✓</span>
        </div>
      </template>
    </div>

    <!-- ===== 底部输入 ===== -->
    <div class="wc-input">
      <div class="ibox">
        <div class="i-mid">
          <input v-model="inputText" class="wc-field" placeholder="输入消息..." @keypress.enter="sendMsg" />
        </div>
        <button class="i-right" :class="{ active: inputText.trim() }" :disabled="!inputText.trim()" @click="sendMsg">
          <svg viewBox="0 0 24 24" width="22" height="22" :fill="inputText.trim() ? '#fce44d' : '#ccc'"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const convId = route.params.id
const convName = route.query.name || '聊天'
const messages = ref([])
const inputText = ref('')
const sending = ref(false)
const msgListRef = ref(null)
let timer = null

const myId = computed(() => userStore.userInfo?.id || null)
const myName = computed(() => userStore.userInfo?.username || '')
const myAvatar = computed(() => userStore.userInfo?.avatar || '')

const isMe = (m) => {
  if (myId.value) return Number(m.sender) === Number(myId.value)
  return m.sender_name === myName.value
}

const avatarColor = (name) => {
  const colors = ['#5c6bc0','#26a69a','#ec407a','#7e57c2','#42a5f5','#ef5350','#66bb6a','#ffa726']
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const loadMessages = async () => {
  try {
    const res = await request.get(`/chat/conversations/${convId}/messages/`)
    messages.value = res?.data || []
  } catch (e) {
    console.error('加载消息失败', e)
    messages.value = []
  } finally { loading.value = false }
}

const scrollBottom = async () => {
  await nextTick()
  if (msgListRef.value) msgListRef.value.scrollTop = msgListRef.value.scrollHeight
}

const sendMsg = async () => {
  const text = inputText.value.trim()
  if (!text || sending.value) return
  sending.value = true
  try {
    await request.post(`/chat/conversations/${convId}/messages/`, { content: text })
    inputText.value = ''
    await loadMessages()
    await scrollBottom()
  } catch (e) { alert('发送失败') }
  finally { sending.value = false }
}

const showTimeGap = (m, idx) => {
  if (idx === 0) return true
  const prev = messages.value[idx - 1]
  if (!prev || !m.created_at || !prev.created_at) return true
  return new Date(m.created_at) - new Date(prev.created_at) > 5 * 60 * 1000
}

const formatTimeSep = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

const formatTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  return String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0')
}

onMounted(async () => {
  await loadMessages()
  await scrollBottom()
  timer = setInterval(async () => {
    await loadMessages()
    await scrollBottom()
  }, 3000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
/* ============================
   整体容器
   ============================ */
.wc-chat {
  display: flex; flex-direction: column;
  height: 100vh; background: #f1f0e8;
  font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans SC", "PingFang SC", sans-serif;
}

/* ============================
   顶部栏
   ============================ */
.wc-header {
  display: flex; align-items: center;
  padding: 10px 12px; background: #fff;
  border-bottom: 1px solid #efefef;
  flex-shrink: 0;
}
.wc-header-left { width: 36px; }
.wc-back { background: none; border: none; font-size: 28px; color: #333; cursor: pointer; padding: 0; line-height: 1; }
.wc-header-mid { flex: 1; text-align: center; }
.wc-header-title { font-size: 16px; font-weight: 600; color: #111; margin: 0; }
.wc-header-right { width: 36px; }

/* ============================
   消息区
   ============================ */
.wc-body {
  flex: 1; overflow-y: auto; overflow-x: hidden;
  padding: 12px 10px 16px; background: #f1f0e8;
}
.wc-time { text-align: center; margin: 14px 0; }
.wc-time p { font-size: 11px; color: #999; margin: 0; }

/* ============================
   消息行 — 对方 / 自己 完全分开
   ============================ */
.msg-row {
  display: flex;
  align-items: flex-end;
  margin: 10px 0;
  gap: 5px;
}
.msg-time {
  font-size: 10px; color: #aaa;
  white-space: nowrap; padding-bottom: 4px;
  flex-shrink: 0;
}

/* ----- 对方消息：左对齐 ----- */
.msg-row.them {
  justify-content: flex-start;
  flex-direction: row;
}

.them-avatar-box { flex-shrink: 0; }
.them-avatar {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600; color: #fff;
  overflow: hidden;
}
.them-avatar p { margin: 0; }

/* 名字 + 气泡 竖向排列 */
.them-msg-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.bubble-name {
  font-size: 10px; color: #999;
  margin: 0 0 3px;
  line-height: 1.2;
  max-width: 120px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}

.them-bubble {
  max-width: 300px; padding: 9px 13px;
  font-size: 14px; line-height: 1.5;
  word-break: break-word; white-space: pre-wrap;
  background: #fff; color: #222;
  border-radius: 0 12px 12px 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.them-bubble p { margin: 0; }

/* ----- 自己消息：右对齐 ----- */
.msg-row.me {
  justify-content: flex-end;
  flex-direction: row;
}

/* 名字 + 气泡 竖向排列 */
.me-msg-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.me-bubble {
  max-width: 300px; padding: 9px 13px;
  font-size: 14px; line-height: 1.5;
  word-break: break-word; white-space: pre-wrap;
  background: #fce44d; color: #222;
  border-radius: 12px 12px 0 12px;
}
.me-bubble p { margin: 0; }

.me-avatar-box { flex-shrink: 0; }
.me-avatar {
  width: 32px; height: 32px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  background: #5c6bc0;
}
.me-avatar p { margin: 0; font-size: 13px; font-weight: 600; color: #fff; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; display: block; }

.msg-read {
  font-size: 10px; color: #aaa;
  padding-bottom: 4px; flex-shrink: 0;
}

/* ============================
   底部输入
   ============================ */
.wc-input {
  flex-shrink: 0; background: #fff;
  border-top: 1px solid #efefef;
  padding: 8px 10px;
}
.ibox {
  display: flex; align-items: center; gap: 6px;
  background: #f2f2f2; border-radius: 20px;
  padding: 4px 6px 4px 16px;
}
.i-mid { flex: 1; }
.wc-field {
  width: 100%; border: none; outline: none;
  background: transparent; font-size: 14px; color: #333;
  padding: 8px 0; min-height: 24px;
}
.wc-field::placeholder { color: #bbb; }
.i-right {
  width: 34px; height: 34px; border-radius: 50%;
  border: none; background: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; flex-shrink: 0;
}
.i-right.active { background: #fce44d; }
.i-right:disabled { cursor: default; }
</style>
