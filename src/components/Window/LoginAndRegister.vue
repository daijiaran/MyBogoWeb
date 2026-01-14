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
  padding: 40px;
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
  color: #f0f0f0;
  z-index: 1000;
  font-family: 'Helvetica Neue', 'Arial', sans-serif;
}

/* ===== 顶部标签（登录 / 注册） ===== */
.auth-tabs {
  display: flex;
  margin-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px 0;
  font-size: 16px;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  background: transparent;
  color: rgba(240, 240, 240, 0.6);
  border: none;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 1px;
  background: rgba(255, 255, 255, 0.8);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.tab-btn.active {
  color: #ffffff;
}

.tab-btn.active::after {
  transform: scaleX(1);
}

.step-title {
  font-size: 18px;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 30px;
  color: #ffffff;
  text-align: center;
}

/* ===== 表单布局 ===== */
.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 24px;
}

label {
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(240, 240, 240, 0.8);
}

input {
  width: 100%;
  padding: 12px 0;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-weight: 300;
  font-size: 16px;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

input::placeholder {
  color: rgba(255, 255, 255, 0.4);
  font-weight: 300;
}

/* ===== 密码格 ===== */
.password-input {
  display: flex;
  align-items: center;
  position: relative;
}

.toggle-pwd {
  position: absolute;
  right: 0;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 0 0;
  cursor: pointer;
  font-size: 12px;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.toggle-pwd:hover {
  color: rgba(255, 255, 255, 0.8);
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

/* ===== 按钮组 ===== */
.btn-group {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.submit-btn {
  flex: 3;
  margin-right: 15px;
  padding: 15px 0;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 14px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn:hover {
  border-color: rgba(255, 255, 255, 0.4);
}

.cancel-btn {
  flex: 2;
  padding: 15px 0;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 14px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.cancel-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.cancel-btn:hover::before {
  left: 100%;
}

.cancel-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  border-color: rgba(255, 255, 255, 0.3);
}

.error-message {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 300;
  font-size: 14px;
}

/* 表单操作区域 */
.form-actions {
  margin-bottom: 10px;
}

.code-actions {
  margin-bottom: 10px;
}

/* 返回注册按钮 */
.back-btn {
  margin-top: 20px;
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.6);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.back-btn::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.8);
  transition: width 0.3s ease;
}

.back-btn:hover {
  color: rgba(255, 255, 255, 0.9);
}

.back-btn:hover::after {
  width: 100%;
}

/* 忘记密码链接 */
.forgot-link {
  display: block;
  margin-bottom: 20px;
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 1px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}

.forgot-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.8);
  transition: width 0.3s ease;
}

.forgot-link:hover {
  color: rgba(255, 255, 255, 0.9);
}

.forgot-link:hover::after {
  width: 100%;
}

/* 验证码描述 */
.code-desc {
  font-size: 12px;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 8px;
  line-height: 1.5;
}

</style>
