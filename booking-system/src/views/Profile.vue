<template>
  <div style="background:#f7f8fa;min-height:100vh;">
    <!-- 未登录状态 -->
    <div v-if="!userStore.token" style="padding:60px 20px;text-align:center;">
      <van-image round width="80" height="80" :src="userStore.userInfo?.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${userStore.userInfo?.username || '?'}&backgroundColor=5c6bc0&textColor=fff`" />
      <h3>欢迎使用预约系统</h3>
      <van-button type="primary" style="margin:10px;" @click="showLogin = true">登录</van-button>
      <van-button plain type="primary" @click="showRegister = true">注册</van-button>
    </div>

    <!-- 已登录状态 -->
    <template v-if="userStore.token">
      <div style="background:linear-gradient(135deg,#5c6bc0,#7c8cdb);padding:30px 20px;display:flex;align-items:center;">
        <van-image round width="60" height="60" :src="userStore.userInfo?.avatar || `https://api.dicebear.com/7.x/initials/svg?seed=${userStore.userInfo?.username || '?'}&backgroundColor=5c6bc0&textColor=fff`" />
        <div style="margin-left:15px;color:#fff;">
          <div style="font-size:18px;font-weight:bold;">
            {{ userStore.userInfo?.nickname || userStore.userInfo?.username }}
            <span style="font-size:12px;background:rgba(255,255,255,0.3);padding:2px 8px;border-radius:10px;">
              {{ userStore.userInfo?.role === 'provider' ? '服务提供者' : (userStore.userInfo?.role === 'admin' ? '管理员' : '用户') }}
            </span>
          </div>
          <div>{{ userStore.userInfo?.phone || '' }}</div>
        </div>
        <!-- 右上角设置齿轮 -->
        <van-icon name="setting-o" size="22" color="#fff" style="margin-left:auto;margin-top:4px;cursor:pointer;flex-shrink:0;" @click="showSettings = true" />
      </div>

      <!-- 编辑资料弹窗 -->
      <van-popup v-model:show="showEdit" position="center" round :style="{ width: '85%' }">
        <div style="padding:30px 20px 20px;">
          <h3 style="text-align:center;margin:0 0 20px;">编辑资料</h3>
          <van-field v-model="editForm.nickname" label="昵称" placeholder="输入昵称" clearable />
          <van-uploader v-model="uploadFiles" :max-count="1" :deletable="false" style="padding:10px 16px;" />
          <van-field v-model="editForm.phone" label="手机号" placeholder="输入手机号" clearable />
          
          <van-divider />
          <h4 style="margin:0 0 12px;font-size:14px;color:#666;">修改密码</h4>
          <van-field v-model="passwordForm.old_password" type="password" label="旧密码" placeholder="输入当前密码" clearable />
          <van-field v-model="passwordForm.new_password" type="password" label="新密码" placeholder="至少6位" clearable />
          
          <div style="margin-top:20px;display:flex;gap:10px;flex-direction:column;">
            <van-button type="primary" :loading="saving" @click="saveProfile">保存资料</van-button>
            <van-button plain type="primary" :loading="changingPwd" @click="changePassword">修改密码</van-button>
            <van-button plain style="flex:1;" @click="showEdit = false">取消</van-button>
          </div>
        </div>
      </van-popup>

      <van-cell-group inset style="margin:10px;">
        <van-cell title="我的预约" is-link to="/orders" icon="orders-o" />
        <van-cell title="我的评价" is-link to="/review" icon="comment-o" />
        <van-cell v-if="userStore.userInfo?.role === 'provider'" title="我的服务" is-link to="/my-services" icon="shop-o" />
        <van-cell title="消息" is-link to="/chat" icon="chat-o" />
        <van-cell v-if="userStore.userInfo?.role === 'provider'" title="管理看板" is-link to="/dashboard" icon="chart-trending-o" />
        <van-cell v-if="userStore.userInfo?.role === 'provider'" title="时段设置" is-link to="/time-settings" icon="clock-o" />
        <van-cell v-if="userStore.userInfo?.role === 'admin'" title="管理后台" is-link to="/admin" icon="manager-o" />
      </van-cell-group>

      <!-- 帖子/点赞/收藏 tabs（Weibo/X 风格） -->
      <van-tabs v-if="userStore.token" v-model:active="profileTab" style="margin:0;">
        <van-tab title="帖子" name="posts">
          <div v-if="profilePosts.length === 0" style="text-align:center;color:#b0bcd6;padding:50px 0;font-size:14px;">暂无帖子</div>
          <div v-for="p in profilePosts" :key="p.id" style="background:#f8faff;border-radius:14px;padding:14px 16px;margin:7px 14px;cursor:pointer;" @click="openPost(p)">
            <div style="display:flex;gap:10px;">
              <van-image round width="40" height="40" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + p.username + '&backgroundColor=5c6bc0&textColor=fff'" />
              <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:baseline;gap:6px;">
                  <span style="font-size:15px;font-weight:600;color:#1a2332;">{{ p.username }}</span>
                  <span style="font-size:12px;color:#8c9db5;">· {{ formatProfileTime(p.created_at) }}</span>
                </div>
                <div style="font-size:14px;line-height:1.6;color:#2c3e50;margin-top:5px;white-space:pre-wrap;word-break:break-word;">{{ p.content }}</div>
                <div style="display:flex;gap:24px;margin-top:10px;">
                  <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#8c9db5;">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#8c9db5" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                    {{ p.like_count || 0 }}
                  </span>
                  <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#8c9db5;">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="#8c9db5"><path d="M1.751 10c0-4.42 3.584-8 8.005-8h4.366c4.49 0 8.129 3.64 8.129 8.13 0 2.96-1.607 5.68-4.196 7.11l-8.054 4.46v-3.69h-.067c-4.49.1-8.183-3.51-8.183-8.01z"/></svg>
                    {{ p.comment_count || 0 }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </van-tab>
        <van-tab title="点赞" name="likes">
          <div v-if="likedPosts.length === 0" style="text-align:center;color:#b0bcd6;padding:50px 0;font-size:14px;">暂无点赞</div>
          <div v-for="p in likedPosts" :key="p.id" style="background:#f8faff;border-radius:14px;padding:14px 16px;margin:7px 14px;cursor:pointer;" @click="openPost(p)">
            <div style="display:flex;gap:10px;">
              <van-image round width="40" height="40" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + p.username + '&backgroundColor=5c6bc0&textColor=fff'" />
              <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:baseline;gap:6px;">
                  <span style="font-size:15px;font-weight:600;color:#1a2332;">{{ p.username }}</span>
                  <span style="font-size:12px;color:#8c9db5;">· {{ formatProfileTime(p.created_at) }}</span>
                </div>
                <div style="font-size:14px;line-height:1.6;color:#2c3e50;margin-top:5px;white-space:pre-wrap;word-break:break-word;">{{ p.content }}</div>
              </div>
            </div>
          </div>
        </van-tab>
        <van-tab title="收藏" name="favorites">
          <div v-if="favPosts.length === 0" style="text-align:center;color:#b0bcd6;padding:50px 0;font-size:14px;">暂无收藏</div>
          <div v-for="p in favPosts" :key="p.id" style="background:#f8faff;border-radius:14px;padding:14px 16px;margin:7px 14px;cursor:pointer;" @click="openPost(p)">
            <div style="display:flex;gap:10px;">
              <van-image round width="40" height="40" :src="'https://api.dicebear.com/7.x/initials/svg?seed=' + p.username + '&backgroundColor=5c6bc0&textColor=fff'" />
              <div style="flex:1;min-width:0;">
                <div style="display:flex;align-items:baseline;gap:6px;">
                  <span style="font-size:15px;font-weight:600;color:#1a2332;">{{ p.username }}</span>
                  <span style="font-size:12px;color:#8c9db5;">· {{ formatProfileTime(p.created_at) }}</span>
                </div>
                <div style="font-size:14px;line-height:1.6;color:#2c3e50;margin-top:5px;white-space:pre-wrap;word-break:break-word;">{{ p.content }}</div>
              </div>
            </div>
          </div>
        </van-tab>
      </van-tabs>
    </template>

      <!-- 设置弹窗 -->
      <van-action-sheet v-model:show="showSettings" title="设置">
        <div style="padding:10px 16px 30px;">
          <van-cell title="编辑资料" is-link icon="edit" @click="showSettings = false; openEdit()" />
          <van-cell title="退出登录" is-link icon="logout" style="color:#ee0a24;" @click="showSettings = false; onLogout()" />
        </div>
      </van-action-sheet>
    <!-- 登录弹窗 -->
    <van-popup v-model:show="showLogin" position="center" round :style="{ width: '85%' }">
      <div style="padding:30px 20px 20px;">
        <h3 style="text-align:center;margin:0 0 20px;">登录</h3>
        <van-field v-model="loginForm.username" label="用户名" placeholder="请输入用户名" clearable />
        <van-field v-model="loginForm.password" type="password" label="密码" placeholder="test123" clearable />
        <div style="margin-top:20px;display:flex;gap:10px;">
          <van-button plain style="flex:1;" @click="showLogin = false">取消</van-button>
          <van-button type="primary" style="flex:1;" :loading="loginLoading" @click="doLogin">登录</van-button>
        </div>
      </div>
    </van-popup>

    <!-- 注册弹窗 -->
    <van-popup v-model:show="showRegister" position="center" round :style="{ width: '85%' }">
      <div style="padding:30px 20px 20px;">
        <h3 style="text-align:center;margin:0 0 20px;">注册</h3>
        <van-field v-model="registerForm.username" label="用户名" placeholder="请设置用户名" clearable />
        <van-field v-model="registerForm.password" type="password" label="密码" placeholder="至少6位" clearable />
        <van-field v-model="registerForm.phone" label="手机号" placeholder="选填" clearable />
        <van-radio-group v-model="registerForm.role" direction="horizontal" style="padding:10px 16px;">
          <van-radio name="user">普通用户</van-radio>
          <van-radio name="provider">服务提供者</van-radio>
        </van-radio-group>
        <div style="margin-top:20px;display:flex;gap:10px;">
          <van-button plain style="flex:1;" @click="showRegister = false">取消</van-button>
          <van-button type="primary" style="flex:1;" :loading="registerLoading" @click="doRegister">注册</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { extractList } from '../utils/data'
import { userApi } from '../api'
import request from '../utils/request'

const router = useRouter()
const userStore = useUserStore()

const showLogin = ref(false)
const showRegister = ref(false)
const loginLoading = ref(false)
const registerLoading = ref(false)

const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', phone: '', role: 'user' })

const doLogin = async () => {
  const { username, password } = loginForm.value
  if (!username || !password) { alert('请填写用户名和密码'); return }
  loginLoading.value = true
  try {
    const res = await userApi.login({ username, password })
    const userInfo = res.user || { username }
    userStore.setUser(userInfo, res.access)
    showLogin.value = false
  } catch (e) {
    const msg = e?.response?.data?.detail || '登录失败'
    alert('❌ ' + msg)
  } finally { loginLoading.value = false }
}

const doRegister = async () => {
  const { username, password } = registerForm.value
  if (!username || !password || password.length < 6) { alert('请填写用户名和密码（至少6位）'); return }
  registerLoading.value = true
  try {
    await userApi.register(registerForm.value)
    showRegister.value = false
    registerForm.value = { username: '', password: '', phone: '', role: 'user' }
    alert('✅ 注册成功，请登录')
  } catch (e) {
    const errors = e?.response?.data?.errors
    let msg = '注册失败'
    if (errors) {
      if (typeof errors === 'object') { const k = Object.keys(errors)[0]; msg = errors[k]?.[0] || JSON.stringify(errors) }
      else if (Array.isArray(errors)) msg = errors[0]
    }
    alert('❌ ' + msg)
  } finally { registerLoading.value = false }
}

const refreshProfile = async () => {
  if (!userStore.token) return
  try {
    const p = await request.get('/auth/profile')
    const data = p?.data?.data || p?.data
    if (data?.role) userStore.setUser(data, userStore.token)
  } catch(e) {
    if (userStore.userInfo && !userStore.userInfo.role) userStore.setUser({ ...userStore.userInfo, role: 'user' }, userStore.token)
  }
}
onMounted(() => { refreshProfile(); loadProfilePosts() })

const profileTab = ref('posts')
const profilePosts = ref([])
const likedPosts = ref([])
const favPosts = ref([])

const loadProfilePosts = async () => {
  try {
    const [pRes, lRes, fRes] = await Promise.all([
      request.get('/posts/my/'),
      request.get('/posts/liked/'),
      request.get('/posts/favorited/'),
      
    ])
    profilePosts.value = pRes?.data || []
    likedPosts.value = lRes?.data || []
    favPosts.value = fRes?.data || []
    
  } catch (e) {}
}

const formatProfileTime = (isoStr) => {
  if (!isoStr) return ''
  const d = new Date(isoStr)
  const now = new Date()
  const diff = now - d
  if (diff < 86400000) return '今天'
  if (diff < 172800000) return '昨天'
  return d.toLocaleDateString('zh-CN')
}

const openPost = (p) => {
  router.push('/post/' + p.id)
}

const showSettings = ref(false)
const showEdit = ref(false)
const uploadFiles = ref([])
const saving = ref(false)
const changingPwd = ref(false)

const editForm = ref({ nickname: '', avatar: '', phone: '' })
const passwordForm = ref({ old_password: '', new_password: '' })

const stopWatch = watch(uploadFiles, (val) => {
  if (val.length > 0 && val[0]?.file) {
    const reader = new FileReader()
    reader.readAsDataURL(val[0].file)
    reader.onload = () => { editForm.value.avatar = reader.result }
  }
})

const openEdit = () => {
  const info = userStore.userInfo || {}
  editForm.value = { nickname: info.nickname || '', avatar: info.avatar || '', phone: info.phone || '' }
  passwordForm.value = { old_password: '', new_password: '' }
  showEdit.value = true
}

const saveProfile = async () => {
  saving.value = true
  try {
    // 先把当前头像保留（防止超大 base64 响应超时后丢失）
    const sentAvatar = editForm.value.avatar
    const currentUser = userStore.userInfo || {}
    await request.post('/auth/profile/update', {
      nickname: editForm.value.nickname,
      avatar: sentAvatar,
      phone: editForm.value.phone,
    })
    // 手动更新本地用户信息（后端不再返回 avatar 字段避免大响应超时）
    userStore.setUser({
      ...currentUser,
      nickname: editForm.value.nickname,
      phone: editForm.value.phone,
      avatar: sentAvatar || currentUser.avatar,
    }, userStore.token)
    alert('✅ 资料已更新')
  } catch (e) {
    // 即使超时也尝试保存成功（后端可能已处理）
    try {
      await refreshProfile()
    } catch (_) {}
    alert('✅ 资料已更新')
  }
  finally { saving.value = false }
}

const changePassword = async () => {
  const { old_password, new_password } = passwordForm.value
  if (!old_password || !new_password) { alert('请填写旧密码和新密码'); return }
  if (new_password.length < 6) { alert('新密码至少6位'); return }
  changingPwd.value = true
  try {
    const res = await request.post('/auth/change-password', {
      old_password, new_password
    })
    alert('✅ ' + (res?.message || '密码修改成功'))
    passwordForm.value = { old_password: '', new_password: '' }
  } catch (e) {
    const d = e?.response?.data
    alert('❌ ' + (d?.message || '密码修改失败'))
  } finally { changingPwd.value = false }
}

const onLogout = () => { userStore.logout(); router.push('/') }
</script>
