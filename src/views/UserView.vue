<template>

  <div class="Mian">
    <div class="user-page">
      <!-- 左侧边栏（桌面端） -->
      <aside class="sidebar" :class="{ hidden: !sidebarVisible }">
        <div class="sidebar-menu">
          <button
              class="menu-item"
              :class="{ active: currentActive === 'home' }"
              @click="currentActive = 'home'"
          >
            <span class="menu-icon"></span>
            <span class="menu-text">主页</span>
          </button>
          <button
              class="menu-item"
              :class="{ active: currentActive === 'personal' }"
              @click="currentActive = 'personal'"
          >
            <span class="menu-icon"></span>
            <span class="menu-text">个人资料</span>
          </button>
          <button
              class="menu-item"
              :class="{ active: currentActive === 'release' }"
              @click="currentActive = 'release'"
          >
            <span class="menu-icon"></span>
            <span class="menu-text">发布</span>
          </button>
          <button
              class="menu-item"
              :class="{ active: currentActive === 'notifications' }"
              @click="currentActive = 'notifications'"
          >
            <span class="menu-icon"></span>
            <span class="menu-text">消息通知</span>
          </button>
        </div>
      </aside>

      <!-- 侧边栏隐藏时：左侧展开按钮（仅桌面端） -->
      <button
          class="toggle-sidebar-btn expand-btn"
          @click="toggleSidebar"
          v-show="!sidebarVisible && windowWidth > 768"
      >
        <span class="menu-icon">{{ buttonIcon }}</span>
        <span class="menu-text">{{ buttonText }}</span>
      </button>

      <!-- 内容区域 -->
      <div class="main-content" :class="{ 'full-width': !sidebarVisible }">
        <!-- 我的主页区域（默认激活） -->
        <div class="home-css" v-if="currentActive === 'home'">
          <!-- 顶部用户信息区 -->
          <header class="user-header">
            <div class="avatar-wrapper">
              <img
                  :src="$img(userAvatar)"
                  alt="用户头像"
                  class="user-avatar"
                  :class="{ 'default-avatar': !userStore.avatarUrl }"
              >
              <!-- 默认头像占位图标 -->
              <span class="default-avatar-icon" v-if="!userStore.avatarUrl">👤</span>
            </div>
            <div class="user-info">
              <h1 class="user-name">{{ userName }}</h1>
              <p class="user-id">ID: {{ userId }}</p>
              <p class="user-status" v-if="loading">加载用户信息中...</p>
              <p class="error-message" v-if="error">{{ error }}</p>
            </div>
          </header>

          <!-- 已发布内容区 -->
          <main class="content-section">
            <load-articles-with-card2-in-user></load-articles-with-card2-in-user>
          </main>
        </div>

        <!-- 个人资料区域 -->
        <div v-if="currentActive === 'personal'" class="background: #0a0a0a">
          <UserEditor></UserEditor>
        </div>

        <!-- 发布区域 -->
        <div v-if="currentActive === 'release'">
          <release-manager class="release-manager"></release-manager>
        </div>

        <!-- 消息通知区域 -->
        <div v-if="currentActive === 'notifications'" class="Notifications-Profile content-section">
          <h2 class="section-title">消息通知</h2>
          <div class="notifications-list">
            <div class="notification-item" style="padding: 15px; border-bottom: 1px solid #555;">
              <p>系统通知：您的内容已通过审核</p>
              <span style="font-size: 0.8rem; color: #999;">10分钟前</span>
            </div>
            <div class="notification-item" style="padding: 15px; border-bottom: 1px solid #555;">
              <p>用户@测试 点赞了您的内容</p>
              <span style="font-size: 0.8rem; color: #999;">1小时前</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/api/user';
import { ElMessage } from 'element-plus';
import userApi from "../api/user";
import ReleaseManager from "../components/User/ReleaseManager.vue";
import LoadArticlesWithCard2InUser from "@/components/Article/LoadArticlesWithCardInUser.vue";
import UserEditor from "../components/User/UserEditor.vue";

const userStore = useUserStore();
const router = useRouter();
const userId = ref('');
const loading = ref(true);
const error = ref('');
const currentActive = ref('home');

// 侧边栏控制相关变量
const sidebarVisible = ref(true); // 控制侧边栏显示/隐藏
const windowWidth = ref(window.innerWidth); // 监听窗口宽度

// 计算属性
const userName = computed(() => userStore.username || '未知用户');
const userAvatar = computed(() => {
  return userStore.avatarUrl ? userStore.avatarUrl : '@/assets/user-avatar.png';
});

// 侧边栏按钮图标和文本
const buttonIcon = computed(() => sidebarVisible.value ? '<-' : '->');
const buttonText = computed(() => sidebarVisible.value ? '隐藏侧边栏' : '展开侧边栏');

// 切换侧边栏显示状态
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value;
};

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth;
  // 移动端自动显示侧边栏（因为移动端是底部导航）
  if (windowWidth.value <= 768) {
    sidebarVisible.value = true;
  }
};

const fetchUserDetails = async () => {
  try {
    loading.value = true;
    error.value = '';
    const response = await userApi.getCurrentUser();
    if (response.data.code !== 200) {
      throw new Error(response.data.message || '获取用户ID失败');
    }
    userId.value = response.data.data.id;
  } catch (err) {
    const errorMsg = err.message || '加载用户信息失败，请刷新页面重试';
    error.value = errorMsg;
    ElMessage.error(errorMsg);
    console.error('获取用户信息失败:', err);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  window.addEventListener('resize', handleResize); // 监听窗口 resize
  await userStore.initUser();
  if (!userStore.isLogin) {
    await router.push('/login');
    ElMessage.warning('请先登录');
    return;
  }
  if (userStore.userId) {
    userId.value = userStore.userId;
    loading.value = false;
  } else {
    await fetchUserDetails();
  }
});

// 组件卸载时移除事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
/* 全局样式重置与基础设置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.home-css {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.Mian{
  padding-top: 60px;
  background: #0a0a0a;
}

/* 整体布局 */
.user-page {
  max-height: calc(100vh - 60PX);
  padding: 20px 20px 20px;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  color: #f0f0f0;
  display: flex;
  gap: 1px;
  background: rgb(10, 10, 10);
  height: 100%;
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

/* 主内容区样式 - 新增过渡效果和宽度控制 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.3s ease;
  background: #0a0a0a;
}

/* 侧边栏隐藏时，内容区全屏显示 */
.main-content.full-width {
  margin-left: 0 !important;
}

/* 用户信息头部 */
.user-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 30px;
  padding: 30px;
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.05);
  word-wrap: break-word;
  width: 100%;
  box-sizing: border-box;
}

.avatar-wrapper {
  flex-shrink: 0;
  position: relative;
}

.user-avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.user-avatar:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

.default-avatar {
  background-color: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.default-avatar-icon {
  position: absolute;
  font-size: 60px;
  color: rgba(255, 255, 255, 0.6);
}

.user-info {
  flex-grow: 1;
}

.user-name {
  margin: 0 0 10px;
  font-size: 2.2rem;
  color: #ffffff;
  font-weight: 300;
  letter-spacing: 1px;
}

.user-id {
  margin: 0 0 15px;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.6);
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: inline-block;
  font-weight: 300;
}

.user-status {
  color: rgba(255, 255, 255, 0.6);
  font-style: italic;
  font-weight: 300;
}

.error-message {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px 12px;
  display: inline-block;
  font-weight: 300;
}

/* 内容区样式 */
.content-section {
  background: #000000;
  border: 1px solid rgb(0, 0, 0);
  padding: 30px;
  min-height: 800px;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  flex: 1;
}

.section-title {
  margin: 0 0 25px;
  font-size: 1.5rem;
  color: #ffffff;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 个人资料、发布、消息通知区域通用样式 */
.profile-content, .release-content, .notifications-list {
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.8);
}

.Personal-Profile {
  color: #f0f0f0;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: #0a0a0a;
  width: 100%;
  padding: 20px;
  box-sizing: border-box;
}

/* 或者更精确的修复 */
.Personal-Profile {
  color: #f0f0f0;
  min-height: 100vh;
  background-color: #0a0a0a;
  width: 100%;
  padding: 0;
}

.Personal-Profile .profile-edit-container {
  padding: 20px;
  min-height: 100vh;
  background-color: #0a0a0a;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item {
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-weight: 300;
}

.notification-item p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
}

.notification-item span {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.5);
}
 /* 左侧边栏样式（桌面端） */
.sidebar {
  width: 240px;
  flex-shrink: 0;
  align-self: flex-start;
  position: sticky;
  top: 20px;
  height: fit-content;
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0;
  padding: 20px 15px;
  box-sizing: border-box;
  transition: all 0.3s ease;
}

/* 侧边栏隐藏状态 */
.sidebar.hidden {
  width: 0;
  padding: 0;
  border: none;
}

.sidebar-menu {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.menu-item {
  width: 100%;
  padding: 15px 18px;
  border: none;
  background: #0a0a0a;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s ease;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
}

.menu-item::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 18px;
  width: 0;
  height: 1px;
  background: rgba(255, 255, 255, 0.5);
  transition: width 0.3s ease;
}

.menu-item:hover {
  color: rgba(255, 255, 255, 0.9);
}

.menu-item:hover::after {
  width: calc(100% - 36px);
}

.menu-item.active {
  color: #ffffff;
}

.menu-item.active::after {
  width: calc(100% - 36px);
  background: rgba(255, 255, 255, 0.8);
}

.menu-icon {
  font-size: 1.2rem;
}

.menu-text {
  font-weight: 300;
}

/* 折叠按钮样式（侧边栏显示时，在侧边栏底部） */
.toggle-sidebar-btn {
  display: flex !important;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.7);
  padding: 12px 16px;
  font-size: 0.9rem;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 0;
}

.toggle-sidebar-btn .menu-icon {
  margin-right: 8px;
}

.toggle-sidebar-btn:hover {
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

/* 展开按钮样式（侧边栏隐藏时，固定在左侧中间） */
.toggle-sidebar-btn.expand-btn {
  position: fixed;
  left: -15px;
  top: 90%;
  transform: translateY(-50%);
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-left: none;
  border-radius: 0 16px 16px 0;
  padding: 18px 20px;
  font-size: 1rem;
  cursor: pointer;
  z-index: 999;
  transition: all 0.3s ease;
  color: rgba(255, 255, 255, 0.7);
  width: auto;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  scale: 70%;
}

.toggle-sidebar-btn.expand-btn .menu-icon {
  margin-right: 0;
  font-size: 1.2rem;
}

.toggle-sidebar-btn.expand-btn .menu-text {
  font-size: 0.85rem;
  white-space: nowrap;
  font-weight: 300;
}

.toggle-sidebar-btn.expand-btn:hover {
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

/* 平板端响应式调整 (769px - 1024px) */
@media (max-width: 1024px) {
  .user-page {
    padding: 20px 30px;
    max-width: 100%;
  }

  .sidebar {
    width: 200px;
    padding: 15px 12px;
  }

  .menu-item {
    padding: 12px 15px;
    font-size: 0.95rem;
    gap: 10px;
  }

  .user-avatar {
    width: 120px;
    height: 120px;
  }

  .user-name {
    font-size: 1.8rem;
  }
}

/* 移动端响应式调整 (≤768px) */
@media (max-width: 768px) {
  .user-page {
    flex-direction: column;
    padding: 15px 15px 0;
    gap: 20px;
    background-color: #000000;
    min-height: 100vh;
    overflow-x: hidden;
  }

  .sidebar {
    position: fixed !important;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100vw;
    max-width: 100%;
    margin-top: 92vh;
    background: #0a0a0a;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px 20px 0 0;
    padding: 10px 15px;
    padding-bottom: calc(10px + env(safe-area-inset-bottom));
    z-index: 999;
    box-sizing: border-box;
    height: auto;
  }

  .sidebar-menu {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 5px;
    background: rgba(255, 255, 255, 0.05);
    align-items: center;
  }

  .menu-item {
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 15px 10px;
    gap: 4px;
    border: none;
    background: transparent;
    border-radius: 10px;
    color: rgba(255, 255, 255, 0.7);
    min-height: 50px;
  }

  /* 隐藏移动端的折叠/展开按钮 */
  .toggle-sidebar-btn, .show-sidebar-btn {
    display: none !important;
  }

  .menu-item.active {
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.1);
  }

  .menu-icon {
    font-size: 1.1rem;
  }

  .main-content {
    padding-bottom: calc(80px + env(safe-area-inset-bottom));
    width: 100%;
    margin: 0 auto;
    box-sizing: border-box;
  }

  .user-header {
    flex-direction: column;
    text-align: center;
    padding: 20px 15px;
    gap: 15px;
    width: 100%;
  }

  .user-avatar {
    width: 100px;
    height: 100px;
  }

  .user-name {
    font-size: 1.5rem;
    color: #ffffff;
    font-weight: 300;
  }

  .content-section {
    padding: 15px 15px 20px 15px;
    min-height: auto;
    width: 100%;
  }

  .Personal-Profile {
    padding: 20px 15px;
    overflow-y: auto;
  }

  .menu-item:active {
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.2);
  }
}

/* 小屏手机优化 (≤480px) */
@media (max-width: 480px) {
  .user-page {
    padding: 8px 8px 0;
  }

  .sidebar {
    padding: 6px 8px;
    padding-bottom: calc(6px + env(safe-area-inset-bottom));
  }

  .sidebar-menu {
    grid-template-columns: repeat(4, 1fr);
    gap: 3px;
  }

  .menu-item {
    font-size: 0.65rem;
    padding: 8px 2px;
    min-height: 48px;
    gap: 3px;
    border-radius: 8px;
  }

  .menu-icon {
    font-size: 0.95rem;
  }

  .main-content {
    padding-bottom: calc(75px + env(safe-area-inset-bottom));
  }

  .user-header {
    padding: 15px 8px;
    gap: 10px;
  }

  .user-avatar {
    width: 80px;
    height: 80px;
  }

  .user-name {
    font-size: 1.2rem;
  }

  .content-section {
    padding: 12px 8px;
  }
}

/* 超小屏手机优化 (≤375px) */
@media (max-width: 375px) {
  .menu-item {
    font-size: 0.6rem;
    padding: 7px 1px;
    min-height: 46px;
  }

  .menu-icon {
    font-size: 0.9rem;
  }

  .user-avatar {
    width: 75px;
    height: 75px;
  }

  .user-name {
    font-size: 1.1rem;
  }
}

.release-content{
  background: #1e1e1e;
  border-radius: 12px;
  padding: 30px;
  min-height: 800px;
  max-height: 90vh;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  flex: 1;
}

.release-manager {
  background: #1e1e1e;
  border-radius: 12px;
  min-height: 800px;
  max-height: 89vh;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  flex: 1;
}
</style>