<template>
  <div class="auth-container">
    <div class="auth-card glass-effect">

      <!-- 标签（登录/注册） -->
      <div class="auth-tabs" v-if="registerStep === 0">
        <button class="tab-btn" :class="{ active: isLoginMode }" @click="switchMode(true)">
          登录
        </button>
        <button class="tab-btn" :class="{ active: !isLoginMode }" @click="switchMode(false)">
          注册
        </button>
      </div>

      <h3 class="step-title" v-if="registerStep === 1">验证邮箱</h3>

      <div v-if="userStore.error" class="error-message">
        {{ userStore.error }}
      </div>

      <!-- 登录 -->
      <form v-if="isLoginMode && registerStep === 0" @submit.prevent="handleLogin" class="auth-form">

        <div class="form-group">
          <label>用户名/邮箱</label>
          <input type="text" v-model="loginForm.emailOrName" required placeholder="请输入用户名或邮箱" @input="clearError">
        </div>

        <div class="form-group">
          <label>密码</label>
          <div class="password-input">
            <input :type="showLoginPwd ? 'text' : 'password'" v-model="loginForm.password" required placeholder="请输入密码" @input="clearError">
            <button type="button" class="toggle-pwd" @click.prevent="showLoginPwd = !showLoginPwd">
              {{ showLoginPwd ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <div class="form-actions">
          <a href="/forgot-password" class="forgot-link">忘记密码?</a>

          <div class="btn-group">
            <button type="submit" class="submit-btn" :disabled="userStore.loading">
              <span v-if="userStore.loading">登录中...</span>
              <span v-else>登录</span>
            </button>

            <button type="button" class="cancel-btn" @click="closeWindow">取消</button>
          </div>
        </div>
      </form>

      <!-- 注册 -->
      <form v-if="!isLoginMode && registerStep === 0" @submit.prevent="handleRegister" class="auth-form">

        <div class="form-group">
          <label>用户名</label>
          <input type="text" v-model="registerForm.name" required minlength="3" maxlength="20" placeholder="请输入3-20位用户名" @input="clearError">
        </div>

        <div class="form-group">
          <label>邮箱</label>
          <input type="email" v-model="registerForm.email" required placeholder="请输入有效的邮箱地址" @input="clearError">
        </div>

        <div class="form-group">
          <label>密码</label>
          <div class="password-input">
            <input :type="showRegisterPwd ? 'text' : 'password'" v-model="registerForm.password" required minlength="6" placeholder="请输入至少6位密码" @input="clearError">
            <button type="button" class="toggle-pwd" @click.prevent="showRegisterPwd = !showRegisterPwd">
              {{ showRegisterPwd ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <div class="btn-group">
          <button type="submit" class="submit-btn" :disabled="userStore.loading">
            <span v-if="userStore.loading">提交中...</span>
            <span v-else>注册并获取验证码</span>
          </button>

          <button type="button" class="cancel-btn" @click="closeWindow">取消</button>
        </div>

      </form>

      <!-- 验证码 -->
      <form v-if="registerStep === 1" @submit.prevent="handleVerifyCode" class="auth-form">
        <div class="form-group">
          <label>验证码</label>
          <input type="text" v-model="verificationCode" required maxlength="6" placeholder="请输入验证码" @input="clearError">

          <div class="code-desc">
            验证码已发送至 {{ userStore.currentRegisterEmail }}，5分钟内有效。
          </div>
        </div>

        <div class="form-actions code-actions">
          <button type="submit" class="submit-btn" :disabled="userStore.loading || !verificationCode">
            <span v-if="userStore.loading">验证中...</span>
            <span v-else>验证并激活</span>
          </button>

          <button type="button" class="cancel-btn" @click="closeWindow">取消</button>
        </div>
      </form>

      <button class="back-btn" v-if="registerStep === 1" @click="goBackToRegister">
        ← 返回注册页
      </button>

    </div>
  </div>
</template>

<script setup>
/* ⭐ 解决 defineEmits 未定义报错 */
import {defineEmits} from 'vue'

import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useUserStore} from '@/api/user'
import {ElMessage} from 'element-plus'

/* ⭐ 使用 defineEmits */
const emit = defineEmits(['close'])

const closeWindow = () => {
  emit('close')
}

const userStore = useUserStore()
const router = useRouter()

const isLoginMode = ref(true)
const registerStep = ref(0)
const verificationCode = ref('')

const loginForm = ref({emailOrName: '', password: ''})
const showLoginPwd = ref(false)

const registerForm = ref({name: '', email: '', password: ''})
const showRegisterPwd = ref(false)

const clearError = () => {
  userStore.error = null
}

const switchMode = (mode) => {
  isLoginMode.value = mode
  registerStep.value = 0
  clearError()
  loginForm.value = {emailOrName: '', password: ''}
  registerForm.value = {name: '', email: '', password: ''}
  verificationCode.value = ''
}

const handleLogin = async () => {
  try {
    const res = await userStore.login(loginForm.value)
    ElMessage.success('登录成功')

    userStore.isLogin = true
    userStore.username = res.user.name
    userStore.avatarUrl = res.user.avatarUrl
    userStore.userId = res.user.id

    await router.push('/user')
  } catch (err) {
    console.log(err)
  }
}

const handleRegister = async () => {
  try {
    await userStore.register(registerForm.value)
    ElMessage.info('验证码已发送')

    registerStep.value = 1
    registerForm.value.password = ''
  } catch (err) {
    console.log(err)
  }
}

const handleVerifyCode = async () => {
  try {
    await userStore.verifyRegistrationCode(verificationCode.value)
    ElMessage.success('验证成功')

    switchMode(true)
    loginForm.value.emailOrName = userStore.currentRegisterEmail
    userStore.currentRegisterEmail = ''
  } catch (err) {
    console.log(err)
  }
}

const goBackToRegister = () => {
  registerStep.value = 0
  verificationCode.value = ''
  clearError()
}
</script>

<style scoped>
/* ===== 弹窗屏幕遮罩（保持暗色，但不占用布局） ===== */
.auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.55); /* 弱化背景 */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999; /* 保证在最上层 */
}

/* ===== 弹窗主体 ===== */
.auth-card {
  width: 380px;
  padding: 28px 26px;
  background: rgba(35, 32, 49, 0.9); /* 深紫半透明玻璃 */
  backdrop-filter: blur(18px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 10px 35px rgba(0,0,0,0.45);
  color: white;
  z-index: 1000;
}

/* ===== 顶部标签（登录 / 注册） ===== */
.auth-tabs {
  display: flex;
  margin-bottom: 20px;
}

.tab-btn {
  flex: 1;
  padding: 12px 0;
  font-size: 16px;
  background: transparent;
  color: #bfbad9;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
}

.tab-btn.active {
  color: #d3c6ff;
  border-bottom: 2px solid #9d72ff;
}

/* ===== 表单布局 ===== */
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 18px;
}

label {
  margin-bottom: 6px;
  font-size: 14px;
  color: #e4dfff;
}

input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.25);
  color: #fff;
}

input::placeholder {
  color: rgba(255,255,255,0.6);
}

/* ===== 密码格 ===== */
.password-input {
  display: flex;
  align-items: center;
  position: relative;
}

.toggle-pwd {
  position: absolute;
  right: 10px;
  background: rgba(255,255,255,0.25);
  border: none;
  padding: 3px 6px;
  border-radius: 4px;
  cursor: pointer;
}

/* ===== 按钮组 ===== */
.btn-group {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

.submit-btn {
  flex: 3;
  margin-right: 8px;
  padding: 10px 0;
  background: #8d5cff;
  border-radius: 8px;
  color: white;
  border: none;
  cursor: pointer;
}

.submit-btn:hover {
  background: #a67bff;
}

.cancel-btn {
  flex: 2;
  padding: 10px 0;
  background: rgba(255,255,255,0.3);
  border-radius: 8px;
  border: none;
  color: white;
  cursor: pointer;
}

.cancel-btn:hover {
  background: rgba(255,255,255,0.45);
}

.error-message {
  background: rgba(255, 90, 90, 0.28);
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 15px;
}

/* 返回注册按钮 */
.back-btn {
  margin-top: 12px;
  font-size: 14px;
  color: #d1c1ff;
  background: none;
  border: none;
  cursor: pointer;
}

</style>
