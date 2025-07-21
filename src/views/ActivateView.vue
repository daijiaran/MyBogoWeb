<template>
  <div class="activation-page">
    <div class="activation-container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>正在验证激活链接...</p>
      </div>

      <!-- 激活成功 -->
      <div v-else-if="success" class="result success">
        <div class="icon">✓</div>
        <h2>账号激活成功！</h2>
        <p>{{ message }}</p>
        <button @click="toLogin" class="btn">前往登录</button>
      </div>

      <!-- 激活失败 -->
      <div v-else-if="error" class="result error">
        <div class="icon">✗</div>
        <h2>激活失败</h2>
        <p>{{ message }}</p>
        <button @click="resendEmail" class="btn secondary">重新发送激活邮件</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

// 状态管理
const loading = ref(true)
const success = ref(false)
const error = ref(false)
const message = ref('')
const router = useRouter()

// 从URL获取激活码
const getActivationCode = () => {
  const searchParams = new URLSearchParams(window.location.search)
  return searchParams.get('code')
}

// 调用后端激活接口
const activateAccount = async (code) => {
  try {
    const response = await axios.get('/api/users/activate', {
      params: { code }
    })
    success.value = true
    message.value = response.data.data.message || '您的账号已成功激活，现在可以登录使用了'
  } catch (err) {
    error.value = true
    // 处理不同错误情况
    if (err.response && err.response.data) {
      message.value = err.response.data.message || '激活链接无效或已过期'
    } else {
      message.value = '网络错误，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

// 重新发送激活邮件（实际项目可能需要获取用户邮箱，这里简化处理）
const resendEmail = async () => {
  // 实际应用中需要先让用户输入注册邮箱
  const email = prompt('请输入您的注册邮箱，我们将重新发送激活链接：')
  if (email) {
    try {
      loading.value = true
      await axios.post('/api/users/forgot-password', null, {
        params: { email }
      })
      message.value = '激活邮件已重新发送，请查收'
    } catch (err) {
      message.value = err.response?.data?.message || '发送失败，请稍后重试'
    } finally {
      loading.value = false
    }
  }
}

// 跳转到登录页
const toLogin = () => {
  router.push('/login')
}

// 页面加载时执行激活
onMounted(() => {
  const code = getActivationCode()
  if (!code) {
    error.value = true
    message.value = '激活链接不完整'
    loading.value = false
    return
  }
  activateAccount(code)
})
</script>

<style scoped>
.activation-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  padding: 20px;
}

.activation-container {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 40px;
  text-align: center;
}

.loading .spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid #42b983;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.result .icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.success .icon {
  color: #42b983;
}

.error .icon {
  color: #e53e3e;
}

h2 {
  margin-bottom: 16px;
  color: #333;
}

p {
  color: #666;
  margin-bottom: 30px;
  font-size: 16px;
}

.btn {
  padding: 12px 30px;
  border-radius: 6px;
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:not(.secondary) {
  background-color: #42b983;
  color: white;
}

.btn:not(.secondary):hover {
  background-color: #359e6d;
}

.btn.secondary {
  background-color: #f0f0f0;
  color: #333;
}

.btn.secondary:hover {
  background-color: #e0e0e0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>