<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- 切换标签（仅登录/注册初始状态显示） -->
      <div class="auth-tabs" v-if="registerStep === 0">
        <button class="tab-btn" :class="{ active: isLoginMode }" @click="switchMode(true)">
          登录
        </button>
        <button class="tab-btn" :class="{ active: !isLoginMode }" @click="switchMode(false)">
          注册
        </button>
      </div>
      <!-- 步骤标题（验证码步骤显示） -->
      <h3 class="step-title" v-if="registerStep === 1">验证邮箱</h3>
      <!-- 错误提示 -->
      <div v-if="userStore.error" class="error-message">
        {{ userStore.error }}
      </div>
      <!-- 登录表单 -->
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
          <button type="submit" class="submit-btn" :disabled="userStore.loading">
            <span v-if="userStore.loading">登录中...</span>
            <span v-else>登录</span>
          </button>
        </div>
      </form>
      <!-- 注册表单（步骤0：填写基本信息） -->
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
        <button type="submit" class="submit-btn" :disabled="userStore.loading">
          <span v-if="userStore.loading">提交中...</span>
          <span v-else>注册并获取验证码</span>
        </button>
      </form>
      <!-- 验证码表单（步骤1：输入验证码） -->
      <form v-if="registerStep === 1" @submit.prevent="handleVerifyCode" class="auth-form">
        <div class="form-group">
          <label>验证码</label>
          <input type="text" v-model="verificationCode" required maxlength="6" placeholder="请输入邮箱收到的6位验证码" @input="clearError" @keyup.enter="handleVerifyCode">
          <div class="code-desc">
            验证码已发送至 {{ userStore.currentRegisterEmail }}，5分钟内有效。未收到？请检查垃圾邮件或稍后重试。
          </div>
        </div>
        <div class="form-actions code-actions">
          <button type="submit" class="submit-btn" :disabled="userStore.loading || !verificationCode">
            <span v-if="userStore.loading">验证中...</span>
            <span v-else>验证并激活</span>
          </button>
        </div>
      </form>
      <!-- 返回按钮（验证码步骤显示） -->
      <button class="back-btn" v-if="registerStep === 1" @click="goBackToRegister">
        ← 返回注册页
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/api/user'
import { ElMessage } from 'element-plus'

// 状态管理
const userStore = useUserStore()
const router = useRouter()

// 表单模式切换
const isLoginMode = ref(true)
// 注册步骤：0=填写注册信息，1=输入验证码
const registerStep = ref(0)
// 验证码输入
const verificationCode = ref('')

// 登录表单数据
const loginForm = ref({
  emailOrName: '',
  password: ''
})
const showLoginPwd = ref(false)

// 注册表单数据
const registerForm = ref({
  name: '',
  email: '',
  password: ''
})
const showRegisterPwd = ref(false)

// 清除错误信息
const clearError = () => {
  userStore.error = null
}

// 切换登录/注册模式
const switchMode = (mode) => {
  isLoginMode.value = mode
  registerStep.value = 0 // 切换时重置注册步骤
  clearError()
  // 清空表单
  loginForm.value = { emailOrName: '', password: '' }
  registerForm.value = { name: '', email: '', password: '' }
  verificationCode.value = ''
}

// 处理登录
const handleLogin = async () => {
  try {
    const loginResult = await userStore.login(loginForm.value);
    ElMessage.success('登录成功');
    // 登录成功后直接更新状态（无需等待initUser）
    userStore.isLogin = true;
    userStore.username = loginResult.user.name;
    userStore.avatarUrl = loginResult.user.avatarUrl;
    userStore.userId = loginResult.user.id;
    router.push('/user'); // 立即跳转
  } catch (err) { /* 错误处理 */ }
};

// 处理注册（提交基本信息后进入验证码步骤）
const handleRegister = async () => {
  try {
    await userStore.register(registerForm.value)
    ElMessage.info('验证码已发送，请查收邮箱')
    registerStep.value = 1 // 切换到验证码步骤
    // 清空注册表单密码（安全考虑）
    registerForm.value.password = ''
  } catch (err) {
    // 错误信息已在store中处理
    console.error('注册失败:', err) // 添加日志以诊断问题
  }
}

// 处理验证码验证（验证成功后切换到登录模式）
const handleVerifyCode = async () => {
  try {
    // 调用验证码验证接口
    await userStore.verifyRegistrationCode(verificationCode.value)
    ElMessage.success('验证成功，账号已激活，请登录')
    // 切换到登录模式
    switchMode(true)
    // 可选：预填邮箱
    loginForm.value.emailOrName = userStore.currentRegisterEmail
    // 清空注册邮箱
    userStore.currentRegisterEmail = ''
  } catch (err) {
    // 错误信息已在store中处理
  }
}

// 返回注册页
const goBackToRegister = () => {
  registerStep.value = 0
  verificationCode.value = ''
  clearError()
}

</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: rgba(245, 245, 245, 0);
  padding: 20px;
}
.auth-card {
  width: 100%;
  max-width: 400px;
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: relative;
}
.step-title {
  text-align: center;
  font-size: 18px;
  color: #333;
  margin: 0 0 20px;
  font-weight: 600;
}
.auth-tabs {
  display: flex;
  margin-bottom: 20px;
}
.tab-btn {
  flex: 1;
  padding: 10px;
  background: transparent;
  border: none;
  border-bottom: 2px solid #eee;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}
.tab-btn.active {
  border-bottom-color: #42b9b9;
  color: #42b983;
  font-weight: bold;
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.form-group label {
  font-size: 14px;
  color: #333;
}
.form-group input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}
.form-group input:focus {
  outline: none;
  border-color: #42b983;
}
.code-desc {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
.password-input {
  display: flex;
  gap: 5px;
}
.password-input input {
  flex: 1;
}
.toggle-pwd {
  padding: 0 10px;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.code-actions {
  margin-top: 10px;
  justify-content: flex-end;
}
.forgot-link {
  color: #42b983;
  text-decoration: none;
  font-size: 14px;
}
.forgot-link:hover {
  text-decoration: underline;
}
.submit-btn {
  padding: 10px 20px;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.3s;
}
.submit-btn:disabled {
  background: #99d9b6;
  cursor: not-allowed;
}
.error-message {
  color: #ff4d4f;
  padding: 10px;
  background: #fff2f0;
  border-radius: 4px;
  margin-bottom: 15px;
  text-align: center;
}
.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  background: transparent;
  border: none;
  color: #42b983;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.back-btn:hover {
  text-decoration: underline;
}
</style>