<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon"><svg viewBox="0 0 40 40" width="48" height="48"><rect x="4" y="6" width="32" height="28" rx="4" fill="none" stroke="#5c6bc0" stroke-width="2.5"/><line x1="4" y1="14" x2="36" y2="14" stroke="#5c6bc0" stroke-width="2"/><line x1="14" y1="4" x2="14" y2="10" stroke="#5c6bc0" stroke-width="2" stroke-linecap="round"/><line x1="26" y1="4" x2="26" y2="10" stroke="#5c6bc0" stroke-width="2" stroke-linecap="round"/><circle cx="13" cy="22" r="2" fill="#5c6bc0"/><circle cx="20" cy="22" r="2" fill="#5c6bc0"/><circle cx="27" cy="22" r="2" fill="#5c6bc0"/><circle cx="13" cy="28" r="2" fill="#5c6bc0"/><circle cx="20" cy="28" r="2" fill="#5c6bc0"/><circle cx="27" cy="28" r="2" fill="#5c6bc0"/></svg></div>
        <h2>预约服务系统</h2>
        <p>欢迎回来，请登录您的账号</p>
      </div>

      <van-form @submit="doLogin">
        <van-cell-group inset>
          <van-field
            v-model="loginForm.username"
            name="username"
            label="用户名"
            placeholder="请输入用户名"
            left-icon="user-o"
            :rules="[{ required: true, message: '请填写用户名' }]"
          />
          <van-field
            v-model="loginForm.password"
            type="password"
            name="password"
            label="密码"
            placeholder="请输入密码"
            left-icon="lock-o"
            :rules="[{ required: true, message: '请填写密码' }]"
          />
        </van-cell-group>

        <div style="margin: 20px 16px;">
          <van-button round block type="primary" native-type="submit" :loading="loading" size="large">
            登 录
          </van-button>
        </div>

        <div class="login-footer">
          <span>还没有账号？</span>
          <span class="link" @click="showRegister = true">立即注册</span>
        </div>
      </van-form>
    </div>

    <!-- 注册弹窗 -->
    <van-popup v-model:show="showRegister" position="center" round :style="{ width: '88%', maxWidth: '420px' }">
      <div class="register-popup">
        <h3>创建账号</h3>
        <van-field v-model="registerForm.username" label="用户名" placeholder="请设置用户名" clearable left-icon="user-o" />
        <van-field v-model="registerForm.password" type="password" label="密码" placeholder="至少6位" clearable left-icon="lock-o" />
        <van-field v-model="registerForm.phone" label="手机号" placeholder="选填" clearable left-icon="phone-o" />
        <div class="role-select">
          <span class="role-label">身份：</span>
          <van-radio-group v-model="registerForm.role" direction="horizontal">
            <van-radio name="user">普通用户</van-radio>
            <van-radio name="provider">服务提供者</van-radio>
          </van-radio-group>
        </div>
        <div class="register-actions">
          <van-button plain block @click="showRegister = false">取消</van-button>
          <van-button type="primary" block :loading="regLoading" @click="doRegister">注册</van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { userApi } from '../api'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const regLoading = ref(false)
const showRegister = ref(false)

const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', phone: '', role: 'user' })

const doLogin = async () => {
  const { username, password } = loginForm.value
  if (!username || !password) {
    alert('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await userApi.login({ username, password })
    const userInfo = res.user || { username }
    userStore.setUser(userInfo, res.access)
    router.push('/')
  } catch (e) {
    const msg = e?.response?.data?.detail || '登录失败，请检查用户名和密码'
    alert('❌ ' + msg)
  } finally {
    loading.value = false
  }
}

const doRegister = async () => {
  const { username, password } = registerForm.value
  if (!username || !password || password.length < 6) {
    alert('请填写用户名和密码（至少6位）')
    return
  }
  regLoading.value = true
  try {
    await userApi.register(registerForm.value)
    showRegister.value = false
    registerForm.value = { username: '', password: '', phone: '', role: 'user' }
    alert('✅ 注册成功，请登录')
  } catch (e) {
    const errors = e?.response?.data?.errors
    let msg = '注册失败'
    if (errors) {
      if (typeof errors === 'object') {
        const firstKey = Object.keys(errors)[0]
        if (firstKey && errors[firstKey]?.length) msg = errors[firstKey][0]
        else msg = JSON.stringify(errors)
      } else if (Array.isArray(errors)) {
        msg = errors[0]
      }
    }
    alert('❌ ' + msg)
  } finally {
    regLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #5c6bc0 0%, #7c8cdb 50%, #9db2f0 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.login-page::before {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  top: -100px;
  right: -100px;
}
.login-page::after {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255,255,255,0.06);
  bottom: -80px;
  left: -80px;
}

.login-card {
  background: #fff;
  border-radius: 20px;
  padding: 36px 28px 28px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}
.login-header .logo-icon {
  font-size: 48px;
  margin-bottom: 8px;
}
.login-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  color: #1a1a2e;
  font-weight: 700;
}
.login-header p {
  margin: 0;
  font-size: 14px;
  color: #969799;
}

.login-card .van-cell-group {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.login-card .van-field {
  padding: 12px 16px;
}

.login-card .van-button--primary {
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 24px;
  background: linear-gradient(135deg, #5c6bc0, #7c8cdb);
  border: none;
}

.login-footer {
  text-align: center;
  color: #969799;
  font-size: 14px;
  margin-top: 8px;
}
.login-footer .link {
  color: #5c6bc0;
  cursor: pointer;
  font-weight: 600;
}
.login-footer .link:hover { text-decoration: underline; }

/* 注册弹窗 */
.register-popup {
  padding: 32px 20px 24px;
}
.register-popup h3 {
  text-align: center;
  margin: 0 0 24px;
  font-size: 20px;
  color: #1a1a2e;
}
.role-select {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
}
.role-label {
  font-size: 14px;
  color: #646566;
  white-space: nowrap;
}
.register-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
.register-actions .van-button {
  flex: 1;
  height: 44px;
  border-radius: 22px;
}
</style>
