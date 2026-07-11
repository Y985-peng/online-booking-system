<template>
  <div class="service-detail-page" style="background:#f7f8fa;min-height:100vh;padding-bottom:80px;">
    <van-loading v-if="loading" style="margin-top:50px;" />

    <template v-if="!loading && service">
      <!-- 顶部服务头图 - 紧凑 -->
      <div style="margin:10px;border-radius:12px;overflow:hidden;">
        
          <div style="height:120px;background:linear-gradient(135deg,#3f51b5,#7c8cdb);color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:600;padding:0 20px;text-align:center;" v-if="!service.image_url">{{ service.name }}</div>
          <van-image width="100%" height="120px" :src="service.image_url" fit="cover" v-if="service.image_url" />
        
      </div>

      <van-cell-group inset style="margin:10px;">
        <van-cell :title="service.name" :label="service.provider_name" />
        <van-cell title="价格" :value="'¥' + service.price + ' / ' + service.duration + '分钟'" />
        <van-cell title="分类" :value="service.category" />
        <van-cell title="地址" :value="service.address" />
        <van-cell title="评分" :value="service.rating + ' 分 (' + service.review_count + ' 条评价)'" />
      </van-cell-group>

      <div style="padding:0 15px;">
        <h4 style="margin-bottom:8px;font-size:15px;">服务介绍</h4>
        <p style="color:#666;line-height:1.6;font-size:14px;">{{ service.description }}</p>
      </div>

      <!-- 评价列表（像这样，是页面内正常元素） -->
      <van-cell-group inset style="margin:10px;">
        <van-cell title="用户评价" />
        <van-cell v-for="r in reviews" :key="r.id" :title="r.username" :label="r.content">
          <template #value>
            <van-rate v-model="r.rating" :size="14" readonly />
          </template>
        </van-cell>
        <van-empty v-if="reviews.length === 0" description="暂无评价" style="padding:20px;" />
      </van-cell-group>

      <!-- 相关帖子 -->
      <van-cell-group inset style="margin:10px;">
        <van-cell title="相关帖子" />
        <template v-for="(p, idx) in displayPosts" :key="p.id">
          <van-cell @click="openPostDetail(p)">
            <template #title>
              <div style="font-size:12px;color:#5c6bc0;font-weight:500;">{{ p.username }}</div>
              <div style="font-size:13px;color:#333;margin-top:4px;line-height:1.4;">{{ p.content }}</div>
              <div v-if="p.service_name" style="font-size:11px;color:#999;margin-top:4px;">关联服务：{{ p.service_name }}</div>
              <div style="font-size:10px;color:#bbb;margin-top:4px;">{{ formatPostTime(p.created_at) }}</div>
            </template>
          </van-cell>
        </template>
        <van-cell v-if="relatedPosts.length > maxShow" is-link :label="showAll ? '收起' : `展开更多 ${relatedPosts.length - maxShow} 条`" @click="togglePosts" />
        <van-empty v-if="relatedPosts.length === 0" description="暂无相关帖子" style="padding:20px;" />
      </van-cell-group>

      <!-- 聊天入口 -->
      <div class="chat-fab" @click.stop="goChat">
        <div style="width:44px;height:44px;border-radius:50%;background:#5c6bc0;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.15);">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="white"><path d="M12 2C6.48 2 2 6.48 2 12c0 1.88.52 3.63 1.42 5.12L2 22l5.15-1.29C8.47 21.52 10.18 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm-1 11H8v-2h3v2zm5 0h-3v-2h3v2z"/></svg>
        </div>
        <span style="font-size:10px;color:#5c6bc0;font-weight:bold;">联系客服</span>
      </div>

      <!-- 预约按钮 — 页面内元素，像评论一样自然在页面底部 -->
      <div style="margin:16px 10px;">
        <van-button type="primary" round block size="large" class="booking-btn" @click="goBooking" style="height:48px;font-size:16px;font-weight:600;">立即预约 · ¥{{ service.price }}</van-button>
      </div>

      <!-- 联系服务提供者 -->
      <div style="margin:0 10px 16px;text-align:center;">
        <span style="color:#969799;font-size:12px;">{{ service.provider_name }} 提供 · {{ service.review_count }} 条评价</span>
      </div>

      <!-- 转发弹窗 -->
      <van-action-sheet v-model:show="showShare" title="转发">
        <div style="padding:10px 16px 30px;">
          <div style="font-size:13px;color:#999;margin-bottom:8px;">转发给好友</div>
          <div style="display:flex;gap:12px;overflow-x:auto;padding-bottom:8px;margin-bottom:16px;">
            <div v-for="c in shareConvs" :key="c.id" style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;flex-shrink:0;" @click="sendToConv(c)">
              <van-image round width="44" height="44" :src="getConvAvatar(c)" />
              <span style="font-size:11px;color:#666;max-width:56px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;">{{ getConvName(c) }}</span>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;flex-shrink:0;" @click="goChat">
              <div style="width:44px;height:44px;border-radius:50%;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:20px;color:#999;border:1px dashed #ccc;">+</div>
              <span style="font-size:11px;color:#666;">新建对话</span>
            </div>
          </div>
          <div style="font-size:13px;color:#999;margin-bottom:8px;">分享到</div>
          <div style="display:flex;gap:12px;margin-bottom:16px;">
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="shareExternal">
              <div style="width:44px;height:44px;border-radius:50%;background:#07c160;display:flex;align-items:center;justify-content:center;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="#fff"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/></svg>
              </div>
              <span style="font-size:11px;color:#666;">微信/QQ</span>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="copyPostLink">
              <div style="width:44px;height:44px;border-radius:50%;background:#5c6bc0;display:flex;align-items:center;justify-content:center;">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="#fff"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
              </div>
              <span style="font-size:11px;color:#666;">复制链接</span>
            </div>
          </div>
        </div>
      </van-action-sheet>

      <!-- 帖子详情弹窗 -->
      <van-popup v-model:show="showPostDetail" position="center" round :style="{ width: '90%', maxHeight: '80vh' }">
        <div v-if="selectedPost" style="padding:20px;overflow-y:auto;max-height:75vh;">
          <!-- 发帖人信息 -->
          <div style="display:flex;align-items:center;margin-bottom:12px;">
            <van-image round width="36" height="36" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + selectedPost.username + '&backgroundColor=5c6bc0&textColor=fff'" />
            <div style="margin-left:10px;">
              <div style="font-size:14px;font-weight:bold;">{{ selectedPost.username }}</div>
              <div style="font-size:11px;color:#969799;">{{ selectedPost.user_role === 'provider' ? '服务提供者' : '用户' }}</div>
            </div>
          </div>
          <!-- 内容 -->
          <div style="font-size:14px;line-height:1.6;white-space:pre-wrap;margin-bottom:16px;">{{ selectedPost.content }}</div>
          <!-- 关联服务 -->
          <div v-if="selectedPost.service_name" style="padding:8px 12px;background:#f0f5ff;border-radius:6px;font-size:13px;color:#5c6bc0;margin-bottom:16px;">
            {{ selectedPost.service_name }}
          </div>
          <!-- 互动按钮 -->
          <div style="display:flex;justify-content:space-around;padding:12px 0;border-top:1px solid #f0f0f0;border-bottom:1px solid #f0f0f0;margin-bottom:16px;">
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="toggleLike">
              <svg viewBox="0 0 24 24" width="24" height="24" :fill="selectedPost.is_liked ? '#ee0a24' : '#999'" :stroke="selectedPost.is_liked ? '#ee0a24' : '#999'" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
              <span style="font-size:11px;color:#999;">{{ selectedPost.like_count || 0 }} 赞</span>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="scrollToComments">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="#999"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              <span style="font-size:11px;color:#999;">{{ selectedPost.comment_count || 0 }} 评论</span>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="toggleFavorite">
              <svg viewBox="0 0 24 24" width="24" height="24" :fill="selectedPost.is_favorited ? '#ffa726' : 'none'" :stroke="selectedPost.is_favorited ? '#ffa726' : '#999'" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              <span style="font-size:11px;color:#999;">{{ selectedPost.favorite_count || 0 }} 收藏</span>
            </div>
            <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="sharePost">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="#999"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/></svg>
              <span style="font-size:11px;color:#999;">转发</span>
            </div>
          </div>
          <!-- 评论区 -->
          <div ref="commentsRef">
            <h4 style="font-size:14px;margin:0 0 10px;">评论 ({{ selectedPost.comment_count || 0 }})</h4>
            <div v-if="postComments.length === 0" style="text-align:center;color:#999;font-size:13px;padding:20px 0;">暂无评论</div>
            <div v-for="c in postComments" :key="c.id" style="padding:8px 0;border-bottom:1px solid #f5f5f5;">
              <div style="font-size:12px;color:#5c6bc0;font-weight:500;">{{ c.username }}</div>
              <div style="font-size:13px;color:#333;margin-top:2px;">{{ c.content }}</div>
              <div style="font-size:10px;color:#bbb;margin-top:2px;">{{ formatPostTime(c.created_at) }}</div>
            </div>
          </div>
          <!-- 评论输入 -->
          <div style="display:flex;gap:8px;margin-top:12px;">
            <van-field v-model="commentText" placeholder="写评论..." :border="true" style="flex:1;border-radius:6px;" />
            <van-button size="small" type="primary" :loading="commenting" @click="submitComment">发送</van-button>
          </div>
          <div style="text-align:center;margin-top:16px;">
            <van-button plain size="small" @click="showPostDetail = false">关闭</van-button>
          </div>
        </div>
      </van-popup>

    </template>
    <van-empty v-if="!loading && !service" description="服务不存在" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import request from '../utils/request'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { serviceApi, reviewApi } from '../api'
import { extractData, extractList } from '../utils/data'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const myName = computed(() => userStore.userInfo?.username || '')

const getConvName = (conv) => {
  const others = (conv.participant_names || []).filter(n => n !== myName.value)
  return others[0] || conv.service_name || '聊天'
}
const getConvAvatar = (conv) => {
  const name = getConvName(conv)
  return 'https://api.dicebear.com/7.x/initials/svg?seed=' + encodeURIComponent(name) + '&backgroundColor=5c6bc0&textColor=fff'
}

const loading = ref(true)
const service = ref(null)
const reviews = ref([])
const relatedPosts = ref([])
const showAll = ref(false)
const maxShow = 2
const showPostDetail = ref(false)
const selectedPost = ref(null)
const postComments = ref([])
const commentText = ref('')
const commenting = ref(false)
const commentsRef = ref(null)

const displayPosts = computed(() => {
  if (showAll.value) return relatedPosts.value
  return relatedPosts.value.slice(0, maxShow)
})

const togglePosts = () => { showAll.value = !showAll.value }

const openPostDetail = async (post) => {
  selectedPost.value = post
  showPostDetail.value = true
  await loadPostComments(post.id)
}

const loadPostComments = async (postId) => {
  try {
    const res = await request.get('/posts/' + postId + '/comments/')
    postComments.value = res?.data || []
  } catch (e) { postComments.value = [] }
}

const toggleLike = async () => {
  if (!selectedPost.value) return
  try {
    const res = await request.post('/posts/' + selectedPost.value.id + '/like/')
    selectedPost.value.is_liked = res.is_liked
    selectedPost.value.like_count = res.like_count
  } catch (e) { alert('操作失败') }
}

const toggleFavorite = async () => {
  if (!selectedPost.value) return
  try {
    const res = await request.post('/posts/' + selectedPost.value.id + '/favorite/')
    selectedPost.value.is_favorited = res.is_favorited
    selectedPost.value.favorite_count = res.favorite_count
  } catch (e) { alert('操作失败') }
}

const submitComment = async () => {
  const text = commentText.value.trim()
  if (!text || !selectedPost.value) return
  commenting.value = true
  try {
    await request.post('/posts/' + selectedPost.value.id + '/comments/', { content: text })
    commentText.value = ''
    await loadPostComments(selectedPost.value.id)
    selectedPost.value.comment_count = (selectedPost.value.comment_count || 0) + 1
  } catch (e) { alert('评论失败') }
  finally { commenting.value = false }
}

// 转发相关
const showShare = ref(false)
const shareConvs = ref([])

const loadShareConvs = async () => {
  try {
    const res = await request.get('/chat/conversations/')
    shareConvs.value = (res?.data || []).slice(0, 5)
  } catch (e) { shareConvs.value = [] }
}

const sharePost = async () => {
  showShare.value = true
  await loadShareConvs()
}

const sendToConv = async (targetUser) => {
  if (!selectedPost.value) return
  try {
    const res = await request.post('/chat/conversations/', {
      service_id: null, provider_id: targetUser.id,
    })
    const convId = res?.data?.id
    if (convId) {
      const text = '[转发] ' + selectedPost.value.content.slice(0, 100)

      await request.post('/chat/conversations/' + convId + '/messages/', { content: text })
      alert('✅ 已转发给 ' + targetUser.username)
      showShare.value = false
    }
  } catch (e) { alert('转发失败') }
}

const shareExternal = async () => {
  const text = selectedPost.value?.content?.slice(0, 100) || ''
  if (navigator.share) {
    try { await navigator.share({ title: '预约系统', text }) } catch (e) {}
  } else {
    try { await navigator.clipboard.writeText(text); alert('内容已复制') }
    catch (e) { prompt('复制以下内容:', text) }
  }
  showShare.value = false
}

const copyPostLink = async () => {
  const url = window.location.origin + '/service/' + route.params.id
  try { await navigator.clipboard.writeText(url); alert('链接已复制') }
  catch (e) { prompt('复制链接:', url) }
  showShare.value = false
}

const scrollToComments = () => {
  // Focus comment input after a short delay
  setTimeout(() => {
    const input = document.querySelector('.van-popup--center .van-field input, .van-popup--center .van-field textarea')
    if (input) input.focus()
  }, 300)
}

const formatPostTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  return d.toLocaleDateString('zh-CN')
}

const loadData = async () => {
  try {
    const id = route.params.id
    const res = await serviceApi.getDetail(id)
    service.value = extractData(res)

    const revRes = await reviewApi.getList(id)
    reviews.value = extractList(revRes)

    // 加载相关帖子
    try {
      const postRes = await request.get('/posts/', { params: { service: id } })
      relatedPosts.value = extractList(postRes)
    } catch (e) { /* ignore */ }
  } catch (e) {
    console.error('加载服务详情失败', e)
    service.value = null
  } finally {
    loading.value = false
  }
}

const goBooking = () => {
  router.push('/booking?service=' + route.params.id + '&name=' + encodeURIComponent(service.value?.name || '') + '&price=' + (service.value?.price || 0))
}

const goChat = async () => {
  if (!service.value) return
  const providerId = service.value.provider
  if (!providerId) { alert('暂无客服'); return }
  try {
    const res = await request.post('/chat/conversations/', {
      service_id: service.value.id,
      provider_id: providerId,
    })
    const convId = res?.data?.id
    if (convId) {
      router.push(`/chat/${convId}?name=${encodeURIComponent(service.value.name)}`)
    }
  } catch (e) {
    alert('连接客服失败')
  }
}

onMounted(loadData)
</script>
