<template>
  <div style="background:#f7f8fa;min-height:100vh;padding-bottom:60px;">
    <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 16px;background:#fff;">
      <h3 style="margin:0;">动态</h3>
      <van-button size="small" type="primary" icon="plus" @click="showCreate = true">发布</van-button>
    </div>

    <div style="padding:8px 12px 4px;background:#fff;">
      <div style="display:flex;align-items:center;background:#f5f5f5;border-radius:20px;padding:0 12px;transition:box-shadow 0.2s;">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="#999"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
        <input v-model="keyword" placeholder="搜索动态..." @keypress.enter="onSearch" style="flex:1;border:none;outline:none;background:transparent;padding:9px 8px;font-size:14px;color:#333;" />
        <van-icon v-if="keyword" name="clear" size="16" color="#bbb" @click="keyword='';onSearch()" style="cursor:pointer;" />
      </div>
    </div>
    <div style="display:flex;gap:6px;padding:0 12px 10px;background:#fff;border-bottom:1px solid #f0f0f0;">
      <span v-for="t in ['最新','最热']" :key="t"
        style="padding:3px 10px;cursor:pointer;font-size:12px;border-radius:10px;transition:all 0.2s;"
        :style="orderByText === t ? 'color:#5c6bc0;background:#eef0f8;font-weight:600;' : 'color:#999;background:transparent;'"
        @click="switchOrder(t)">{{ t }}</span>
    </div>

    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
    <van-loading v-if="loading" style="margin-top:50px;" />

    <template v-if="!loading">
      <van-empty v-if="posts.length === 0" :description="keyword ? '\u672a\u627e\u5230\u76f8\u5173\u52a8\u6001' : '\u6682\u65e0\u52a8\u6001'" />

      <div v-for="p in posts" :key="p.id" style="background:#fff;margin:8px 0;padding:14px;">
        <!-- 用户信息 -->
        <div style="display:flex;align-items:center;margin-bottom:8px;">
          <van-image round width="36" height="36" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + p.username + '&backgroundColor=5c6bc0&textColor=fff'" />
          <div style="margin-left:10px;flex:1;">
            <div style="font-size:14px;font-weight:bold;">{{ p.username }}</div>
            <div style="font-size:11px;color:#969799;">{{ p.user_role === 'provider' ? '服务提供者' : '用户' }}</div>
          </div>
        </div>
        <!-- 内容（可点击打开详情） -->
        <div style="font-size:14px;line-height:1.6;white-space:pre-wrap;cursor:pointer;" @click="openPostDetail(p)">{{ p.content }}</div>
        <!-- 关联服务 -->
        <div v-if="p.service_id" style="margin-top:10px;padding:10px;background:#f0f5ff;border-radius:6px;display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:13px;color:#5c6bc0;">{{ p.service_name }}</span>
          <van-button size="mini" type="primary" @click="$router.push('/booking?service=' + p.service_id + '&name=' + encodeURIComponent(p.service_name || ''))">预约</van-button>
        </div>
        <!-- 互动按钮 -->
        <div style="display:flex;justify-content:space-around;padding:8px 0 0;border-top:1px solid #f0f0f0;margin-top:8px;" @click.stop>
          <div style="display:flex;align-items:center;gap:4px;cursor:pointer;font-size:12px;color:#999;" @click.stop.prevent="toggleLike(p)">
            <svg viewBox="0 0 24 24" width="16" height="16" :fill="p.is_liked ? '#ee0a24' : 'none'" :stroke="p.is_liked ? '#ee0a24' : '#999'" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            {{ p.like_count || 0 }}
          </div>
          <div style="display:flex;align-items:center;gap:4px;cursor:pointer;font-size:12px;color:#999;" @click.stop.prevent="openPostDetail(p)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="#999"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            {{ p.comment_count || 0 }}
          </div>
          <div style="display:flex;align-items:center;gap:4px;cursor:pointer;font-size:12px;color:#999;" @click.stop.prevent="toggleFavorite(p)">
            <svg viewBox="0 0 24 24" width="16" height="16" :fill="p.is_favorited ? '#ffa726' : 'none'" :stroke="p.is_favorited ? '#ffa726' : '#999'" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            {{ p.favorite_count || 0 }}
          </div>
          <div style="display:flex;align-items:center;gap:4px;cursor:pointer;font-size:12px;color:#999;" @click.stop.prevent="showShareDialog(p)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="#999"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/></svg>
            转发
          </div>
          <div v-if="isAdmin" style="display:flex;align-items:center;gap:4px;cursor:pointer;font-size:12px;color:#ee0a24;" @click.stop.prevent="deleteFeedPost(p)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="#ee0a24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
            删除
          </div>
        </div>
      </div>
    </template>

        </van-pull-refresh>

    <!-- ===== 帖子详情弹窗 ===== -->
    <van-popup v-model:show="showPostDetail" position="center" round :style="{ width: '90%', maxHeight: '80vh' }">
      <div v-if="selectedPost" style="padding:20px;overflow-y:auto;max-height:75vh;">
        <div style="display:flex;align-items:center;margin-bottom:12px;">
          <van-image round width="36" height="36" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + selectedPost.username + '&backgroundColor=5c6bc0&textColor=fff'" />
          <div style="margin-left:10px;">
            <div style="font-size:14px;font-weight:bold;">{{ selectedPost.username }}</div>
            <div style="font-size:11px;color:#969799;">{{ selectedPost.user_role === 'provider' ? '服务提供者' : '用户' }}</div>
          </div>
        </div>
        <div style="font-size:14px;line-height:1.6;white-space:pre-wrap;margin-bottom:16px;">{{ selectedPost.content }}</div>
        <div v-if="selectedPost.service_name" style="padding:8px 12px;background:#f0f5ff;border-radius:6px;font-size:13px;color:#5c6bc0;margin-bottom:16px;">
          {{ selectedPost.service_name }}
        </div>
        <div style="display:flex;justify-content:space-around;padding:12px 0;border-top:1px solid #f0f0f0;border-bottom:1px solid #f0f0f0;margin-bottom:16px;">
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="toggleLikeDetail">
            <svg viewBox="0 0 24 24" width="24" height="24" :fill="selectedPost.is_liked ? '#ee0a24' : 'none'" :stroke="selectedPost.is_liked ? '#ee0a24' : '#999'" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            <span style="font-size:11px;color:#999;">{{ selectedPost.like_count || 0 }} 赞</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="focusComment">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="#999"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span style="font-size:11px;color:#999;">{{ selectedPost.comment_count || 0 }} 评论</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click="toggleFavoriteDetail">
            <svg viewBox="0 0 24 24" width="24" height="24" :fill="selectedPost.is_favorited ? '#ffa726' : 'none'" :stroke="selectedPost.is_favorited ? '#ffa726' : '#999'" stroke-width="1.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            <span style="font-size:11px;color:#999;">{{ selectedPost.favorite_count || 0 }} 收藏</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click.stop.prevent="showShareDialog(selectedPost)">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="#999"><path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/></svg>
            <span style="font-size:11px;color:#999;">转发</span>
          </div>
          <div v-if="isAdmin" style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;" @click.stop.prevent="deleteDetailPost">
            <svg viewBox="0 0 24 24" width="24" height="24" fill="#ee0a24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
            <span style="font-size:11px;color:#ee0a24;">删除</span>
          </div>
        </div>
        <div ref="commentsRef">
          <h4 style="font-size:14px;margin:0 0 10px;">评论 ({{ selectedPost.comment_count || 0 }})</h4>
          <div v-if="postComments.length === 0" style="text-align:center;color:#999;font-size:13px;padding:20px 0;">暂无评论</div>
          <div v-for="c in postComments" :key="c.id" style="padding:8px 0;border-bottom:1px solid #f5f5f5;">
            <div style="font-size:12px;color:#5c6bc0;font-weight:500;">{{ c.username }}</div>
            <div style="font-size:13px;color:#333;margin-top:2px;">{{ c.content }}</div>
            <div style="font-size:10px;color:#bbb;margin-top:2px;">{{ formatPostTime(c.created_at) }}</div>
          </div>
        </div>
        <div style="display:flex;gap:8px;margin-top:12px;">
          <van-field v-model="commentText" placeholder="写评论..." :border="true" style="flex:1;border-radius:6px;" />
          <van-button size="small" type="primary" :loading="commenting" @click="submitComment">发送</van-button>
        </div>
        <div style="text-align:center;margin-top:16px;">
          <van-button plain size="small" @click="showPostDetail = false">关闭</van-button>
        </div>
      </div>
    </van-popup>

    <!-- ===== 转发弹窗 ===== -->
    <van-action-sheet v-model:show="showShare" title="转发">
      <div style="padding:10px 16px 30px;">
        <!-- 转发给好友 -->
        <div style="font-size:13px;color:#999;margin-bottom:8px;">转发给好友</div>
        <div style="display:flex;gap:12px;overflow-x:auto;padding-bottom:8px;margin-bottom:16px;">
          <div v-for="c in shareConvs" :key="c.id" style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;flex-shrink:0;" @click="sendToConv(c)">
            <div style="width:44px;height:44px;border-radius:50%;background:#5c6bc0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:16px;font-weight:600;">
              {{ c.service_name?.charAt(0) || '?' }}
            </div>
            <span style="font-size:11px;color:#666;max-width:56px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:center;">{{ c.service_name || '聊天' }}</span>
          </div>
          <div style="display:flex;flex-direction:column;align-items:center;gap:4px;cursor:pointer;flex-shrink:0;" @click="goChat">
            <div style="width:44px;height:44px;border-radius:50%;background:#f0f0f0;display:flex;align-items:center;justify-content:center;font-size:20px;color:#999;border:1px dashed #ccc;">+</div>
            <span style="font-size:11px;color:#666;">新建对话</span>
          </div>
        </div>
        <!-- 外部转发 -->
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

    <!-- 发布弹窗 -->
    <van-popup v-model:show="showCreate" position="bottom" round style="max-height:70%;">
      <div style="padding:20px;">
        <h3 style="margin:0 0 15px;text-align:center;">发布动态</h3>
        <van-field v-model="form.content" type="textarea" rows="5" placeholder="分享你的想法..." />
        <van-field label="关联服务" is-link readonly :model-value="form.svcName || '不关联'" @click="showPicker = true" />
        <div style="margin-top:15px;">
          <van-button round block type="primary" :loading="submitting" @click="onSubmit">发布</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 服务选择器 -->
    <van-popup v-model:show="showPicker" position="bottom" round>
      <div style="padding:16px 20px 30px;max-height:55vh;overflow-y:auto;">
        <h3 style="text-align:center;margin:0 0 12px;">选择关联服务</h3>
        <div style="display:flex;align-items:center;background:#f5f5f5;border-radius:8px;padding:0 10px;margin-bottom:10px;">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="#999"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
          <input v-model="svcSearch" placeholder="搜索服务..." style="flex:1;border:none;outline:none;background:transparent;padding:10px 8px;font-size:14px;color:#333;" />
          <van-icon v-if="svcSearch" name="clear" size="16" color="#bbb" @click="svcSearch=''" />
        </div>
        <div style="padding:12px 16px;font-size:14px;border-bottom:1px solid #f5f5f5;cursor:pointer;" @click="pickService(null)">不关联服务</div>
        <div v-for="s in filteredServices" :key="s.id" style="padding:12px 16px;font-size:14px;color:#5c6bc0;border-bottom:1px solid #f5f5f5;cursor:pointer;" @click="pickService(s)">{{ s.name }}</div>
        <div v-if="filteredServices.length === 0" style="text-align:center;color:#999;padding:20px 0;">无匹配服务</div>
        <van-button plain block style="margin-top:12px;" @click="showPicker = false">取消</van-button>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { serviceApi } from '../api'
import { extractList } from '../utils/data'
import request from '../utils/request'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()
const myName = computed(() => userStore.userInfo?.username || '')
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const getConvName = (conv) => {
  const others = (conv.participant_names || []).filter(n => n !== myName.value)
  return others[0] || conv.service_name || '聊天'
}
const getConvAvatar = (conv) => {
  const name = getConvName(conv)
  return 'https://api.dicebear.com/7.x/initials/svg?seed=' + encodeURIComponent(name) + '&backgroundColor=5c6bc0&textColor=fff'
}

const loading = ref(true)
const posts = ref([])
const allServices = ref([])
const svcSearch = ref('')
const filteredServices = computed(() => {
  if (!svcSearch.value) return allServices.value
  const q = svcSearch.value.toLowerCase()
  return allServices.value.filter(s => (s.name || '').toLowerCase().includes(q))
})
const showCreate = ref(false)
const showPicker = ref(false)
const submitting = ref(false)
const form = ref({ content: '', service_id: null, svcName: '' })
const keyword = ref('')
const refreshing = ref(false)
const orderByText = ref('最新')
const orderBy = ref('-created_at')

// 帖子详情
const showPostDetail = ref(false)
const selectedPost = ref(null)
const postComments = ref([])
const commentText = ref('')
const commenting = ref(false)
const commentsRef = ref(null)

// 转发
const showShare = ref(false)
const sharePostData = ref(null)
const shareConvs = ref([])

const loadShareConvs = async () => {
  try {
    const res = await request.get('/chat/conversations/')
    shareConvs.value = (res?.data || []).slice(0, 5)
  } catch (e) { shareConvs.value = [] }
}

/* ---- 加载 ---- */
const loadPosts = async () => {
  try {
    const res = await serviceApi.getList({})
    allServices.value = extractList(res)
  } catch (e) { console.error(e) }
  try {
    const params = {}
    if (keyword.value) params.search = keyword.value
    if (orderBy.value) params.ordering = orderBy.value
    const res = await request.get('/posts/', { params })
    posts.value = res?.data || []
  } catch (e) { console.error(e) }
  loading.value = false
}

const pickService = (s) => {
  form.value.service_id = s?.id || null
  form.value.svcName = s?.name || ''
  showPicker.value = false
}

const onSubmit = async () => {
  if (!form.value.content.trim()) { alert('请输入内容'); return }
  submitting.value = true
  try {
    await request.post('/posts/', { content: form.value.content, service_id: form.value.service_id })
    showCreate.value = false
    form.value = { content: '', service_id: null, svcName: '' }
    await loadPosts()
  } catch (e) { alert('发布失败') }
  submitting.value = false
}

/** 更新时间显示 */

const onSearch = () => { loadPosts() }

const onRefresh = () => { refreshing.value = true; loadPosts() }

const switchOrder = (t) => {
  orderByText.value = t
  orderBy.value = t === '最热' ? '-like_count' : '-created_at'
  loadPosts()
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

/** 刷新单条帖子数据 */
const refreshPost = async (postId) => {
  try {
    const res = await request.get('/posts/' + postId + '/')
    const updated = res?.data
    if (updated) {
      const idx = posts.value.findIndex(p => p.id === postId)
      if (idx >= 0) posts.value[idx] = updated
    }
  } catch (e) {}
}

/* ---- 帖子详情 ---- */
const openPostDetail = async (post) => {
  selectedPost.value = { ...post }
  showPostDetail.value = true
  try {
    const res = await request.get('/posts/' + post.id + '/')
    if (res?.data) selectedPost.value = res.data
    const cRes = await request.get('/posts/' + post.id + '/comments/')
    postComments.value = cRes?.data || []
  } catch (e) { postComments.value = [] }
}

const focusComment = () => {
  setTimeout(() => {
    const input = document.querySelector('.van-popup--center .van-field input, .van-popup--center .van-field textarea')
    if (input) input.focus()
  }, 300)
}

/* ---- 点赞 ---- */
const toggleLike = async (p) => {
  try {
    const res = await request.post('/posts/' + p.id + '/like/')
    if (res) {
      p.is_liked = res.is_liked
      p.like_count = res.like_count
    }
  } catch (e) {
    console.error('点赞失败:', e?.response?.data || e.message)
  }
}
const toggleLikeDetail = async () => {
  if (!selectedPost.value) return
  await toggleLike(selectedPost.value)
  refreshPost(selectedPost.value.id)
}

/* ---- 收藏 ---- */
const toggleFavorite = async (p) => {
  try {
    const res = await request.post('/posts/' + p.id + '/favorite/')
    p.is_favorited = res.is_favorited
    p.favorite_count = res.favorite_count
  } catch (e) {}
}
const toggleFavoriteDetail = async () => {
  if (!selectedPost.value) return
  await toggleFavorite(selectedPost.value)
  refreshPost(selectedPost.value.id)
}

/* ---- 评论 ---- */
const submitComment = async () => {
  const text = commentText.value.trim()
  if (!text || !selectedPost.value) return
  commenting.value = true
  try {
    await request.post('/posts/' + selectedPost.value.id + '/comments/', { content: text })
    commentText.value = ''
    const res = await request.get('/posts/' + selectedPost.value.id + '/comments/')
    postComments.value = res?.data || []
    selectedPost.value.comment_count = (selectedPost.value.comment_count || 0) + 1
    refreshPost(selectedPost.value.id)
  } catch (e) { alert('评论失败') }
  finally { commenting.value = false }
}

/* ---- 转发 ---- */
const showShareDialog = async (post) => {
  sharePostData.value = post
  showShare.value = true
  await loadShareConvs()
}

const sendToConv = async (targetUser) => {
  if (!sharePostData.value) return
  try {
    const res = await request.post('/chat/conversations/', {
      service_id: null,
      provider_id: targetUser.id,
    })
    const convId = res?.data?.id
    if (convId) {
      const text = '转发帖子:\n' + sharePostData.value.content.slice(0, 100)
      await request.post('/chat/conversations/' + convId + '/messages/', { content: text })
      alert('✅ 已转发给 ' + targetUser.username)
      showShare.value = false
    }
  } catch (e) { alert('转发失败') }
}

const shareExternal = async () => {
  const text = sharePostData.value?.content?.slice(0, 100) || ''
  if (navigator.share) {
    try { await navigator.share({ title: '预约系统', text }) } catch (e) {}
  } else {
    try {
      await navigator.clipboard.writeText(text)
      alert('内容已复制，可粘贴到微信/QQ')
    } catch (e) { prompt('复制以下内容分享到微信/QQ:', text) }
  }
  showShare.value = false
}

const copyLink = async () => {
  const url = window.location.origin + '/service/' + (sharePostData.value?.service_id || '')
  try {
    await navigator.clipboard.writeText(url)
    alert('链接已复制')
  } catch (e) { prompt('复制链接:', url) }
  showShare.value = false
}

onMounted(loadPosts)

const deleteDetailPost = async () => {
  if (userStore.userInfo?.role !== 'admin') return
  if (!selectedPost.value || !confirm('确定删除此帖子？')) return
  try {
    await request.post('/posts/' + selectedPost.value.id + '/reject/')
    showPostDetail.value = false
    await loadPosts()
  } catch (e) { alert('删除失败') }
}

const deleteFeedPost = async (post) => {
  if (userStore.userInfo?.role !== 'admin') return
  if (!confirm('确定删除此帖子？')) return
  try {
    await request.post('/posts/' + post.id + '/reject/')
    await loadPosts()
  } catch (e) { alert('删除失败') }
}
</script>
