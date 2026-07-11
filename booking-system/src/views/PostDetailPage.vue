<template>
  <div style="background:#f7f8fa;min-height:100vh;padding-bottom:80px;">
    <van-nav-bar title="帖子详情" left-arrow @click-left="router.back()" />

    <van-loading v-if="loading" style="margin-top:50px;" />

    <template v-if="!loading && post">
      <!-- 用户信息 -->
      <div style="background:#fff;padding:16px;display:flex;align-items:center;">
        <van-image round width="40" height="40" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + post.username + '&backgroundColor=5c6bc0&textColor=fff'" />
        <div style="margin-left:12px;">
          <div style="font-size:15px;font-weight:600;">{{ post.username }}</div>
          <div style="font-size:11px;color:#bbb;">{{ formatTime(post.created_at) }}</div>
        </div>
      </div>

      <!-- 内容 -->
      <div style="background:#fff;padding:0 16px 16px;font-size:15px;line-height:1.6;white-space:pre-wrap;word-break:break-word;">{{ post.content }}</div>

      <!-- 关联服务 -->
      <div v-if="post.service_id" style="margin:10px;padding:12px;background:#f0f5ff;border-radius:8px;display:flex;justify-content:space-between;align-items:center;">
        <div>
          <div style="font-size:12px;color:#999;">关联服务</div>
          <div style="font-size:14px;color:#5c6bc0;font-weight:500;">{{ post.service_name }}</div>
        </div>
        <van-button size="small" type="primary" round @click="goBooking">立即预约</van-button>
      </div>

      <!-- 互动按钮 -->
      <div style="background:#fff;margin:10px;border-radius:8px;padding:12px 0;display:flex;justify-content:space-around;">
        <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="toggleLike">
          <svg viewBox="0 0 24 24" width="24" height="24" :fill="post.is_liked ? '#ee0a24' : 'none'" :stroke="post.is_liked ? '#ee0a24' : '#999'" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          <span style="font-size:11px;color:#999;">{{ post.like_count || 0 }} 赞</span>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="focusComment">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="#999"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span style="font-size:11px;color:#999;">{{ post.comment_count || 0 }} 评论</span>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="toggleFavorite">
          <svg viewBox="0 0 24 24" width="24" height="24" :fill="post.is_favorited ? '#ffa726' : 'none'" :stroke="post.is_favorited ? '#ffa726' : '#999'" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          <span style="font-size:11px;color:#999;">{{ post.favorite_count || 0 }} 收藏</span>
        </div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="sharePost">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="#999"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/></svg>
          <span style="font-size:11px;color:#999;">转发</span>
        </div>
        <div v-if="isAdmin" style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="deletePost">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="#ee0a24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
          <span style="font-size:11px;color:#ee0a24;">删除</span>
        </div>
      </div>

      <!-- 评论 -->
      <div style="background:#fff;margin:10px;border-radius:8px;padding:16px;">
        <h4 style="font-size:14px;margin:0 0 12px;">评论 ({{ post.comment_count || 0 }})</h4>
        <div v-if="comments.length === 0" style="text-align:center;color:#999;font-size:13px;padding:20px 0;">暂无评论</div>
        <div v-for="c in comments" :key="c.id" style="padding:10px 0;border-bottom:1px solid #f5f5f5;">
          <div style="font-size:12px;color:#5c6bc0;font-weight:500;">{{ c.username }}</div>
          <div style="font-size:13px;color:#333;margin-top:3px;">{{ c.content }}</div>
          <div style="font-size:10px;color:#bbb;margin-top:3px;">{{ formatTime(c.created_at) }}</div>
        </div>
        <div style="display:flex;gap:8px;margin-top:12px;">
          <van-field v-model="commentText" placeholder="写评论..." :border="true" style="flex:1;border-radius:6px;" />
          <van-button size="small" type="primary" :loading="commenting" @click="submitComment">发送</van-button>
        </div>
      </div>
    </template>

    <!-- 转发弹窗 -->
    <van-action-sheet v-model:show="showShare" title="转发">
      <div style="padding:10px 16px 30px;">
        <div style="font-size:13px;color:#999;margin-bottom:8px;">分享到</div>
        <div style="display:flex;gap:12px;margin-bottom:16px;">
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="shareExternal">
            <div style="width:44px;height:44px;border-radius:50%;background:#07c160;display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="#fff"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/></svg>
            </div>
            <span style="font-size:11px;color:#666;">微信/QQ</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="copyLink">
            <div style="width:44px;height:44px;border-radius:50%;background:#5c6bc0;display:flex;align-items:center;justify-content:center;">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="#fff"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
            </div>
            <span style="font-size:11px;color:#666;">复制链接</span>
          </div>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import request from '../utils/request'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const loading = ref(true)
const post = ref(null)
const comments = ref([])
const commentText = ref('')
const commenting = ref(false)
const showShare = ref(false)

const loadPost = async () => {
  try {
    const res = await request.get('/posts/' + route.params.id + '/')
    post.value = res?.data
    const cRes = await request.get('/posts/' + route.params.id + '/comments/')
    comments.value = cRes?.data || []
  } catch (e) { post.value = null }
  finally { loading.value = false }
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

const toggleLike = async () => {
  if (!post.value) return
  try {
    const res = await request.post('/posts/' + post.value.id + '/like/')
    post.value.is_liked = res.is_liked
    post.value.like_count = res.like_count
  } catch (e) {}
}

const toggleFavorite = async () => {
  if (!post.value) return
  try {
    const res = await request.post('/posts/' + post.value.id + '/favorite/')
    post.value.is_favorited = res.is_favorited
    post.value.favorite_count = res.favorite_count
  } catch (e) {}
}

const submitComment = async () => {
  const text = commentText.value.trim()
  if (!text || !post.value) return
  commenting.value = true
  try {
    await request.post('/posts/' + post.value.id + '/comments/', { content: text })
    commentText.value = ''
    const res = await request.get('/posts/' + post.value.id + '/comments/')
    comments.value = res?.data || []
    post.value.comment_count = (post.value.comment_count || 0) + 1
  } catch (e) { alert('评论失败') }
  finally { commenting.value = false }
}

const focusComment = () => {
  const input = document.querySelector('.van-field input, .van-field textarea')
  if (input) input.focus()
}

const sharePost = () => { showShare.value = true }

const deletePost = async () => {
  if (!confirm('确定删除此帖子？')) return
  try {
    await request.post('/posts/' + route.params.id + '/reject/')
    alert('已删除')
    router.back()
  } catch (e) { alert('删除失败') }
}

const shareExternal = async () => {
  const text = post.value?.content?.slice(0, 100) || ''
  if (navigator.share) {
    try { await navigator.share({ title: '预约系统', text }) } catch (e) {}
  } else {
    try { await navigator.clipboard.writeText(text); alert('内容已复制') }
    catch (e) { prompt('复制以下内容:', text) }
  }
  showShare.value = false
}

const copyLink = async () => {
  const url = window.location.origin + '/post/' + route.params.id
  try { await navigator.clipboard.writeText(url); alert('链接已复制') }
  catch (e) { prompt('复制链接:', url) }
  showShare.value = false
}

const goBooking = () => {
  if (post.value?.service_id) {
    router.push('/booking?service=' + post.value.service_id + '&name=' + encodeURIComponent(post.value.service_name || ''))
  }
}

onMounted(loadPost)
</script>
