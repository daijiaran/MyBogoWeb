<template>
  <template v-if="!isQuizMode">
    <header class="navbar">
      <button
          class="back-btn"
          v-if="isCollapsed"
          @click="handleBack"
      >
        ← 返回
      </button>

      <transition name="navbar-anim">
        <div
            class="nav"
            :class="{ 'collapsed': isCollapsed }"
            v-show="true"
        >
          <span class="title-logo" v-if="!isCollapsed">DigitalMaker</span>

          <nav class="desktop-nav" v-if="!isCollapsed">
            <router-link
                v-for="item in menuItems"
                :key="item.id"
                :to="item.path"
                :style="{ 'margin': `0 ${itemGap}px` }"
                class="nav-link"
            >
              {{ item.title }}
            </router-link>
          </nav>

          <div class="hamburger" @click.stop="toggleMenu" style="display: none;">
            <div class="hamburger-icon" />
          </div>

          <transition name="slide-down" appear>
            <nav v-show="isMenuOpen" class="mobile-nav" style="display: none;">
              <router-link
                  v-for="item in menuItems"
                  :key="item.id"
                  :to="item.path"
                  class="mobile-link"
                  @click="closeMenu"
              >
                {{ item.title }}
              </router-link>
            </nav>
          </transition>
        </div>
      </transition>
    </header>

    <div class="user-btn" @click.stop="handleAvatarClick" v-if="!isCollapsed">
      <span v-if="!isLogin" class="login-text">登录</span>
      <img
          v-else
          :src="userAvatar"
          alt="用户头像"
          class="avatar-img"
      >
    </div>
  </template>

  <div v-else class="quiz-home-btn-container">
    <button class="quiz-home-btn" @click="goHome">
      🏠 返回首页
    </button>
  </div>

  <transition name="fade-in" appear>
    <div v-if="isPopupOpen" class="popup-container">
      <div class="popup-mask" @click="closePopup"></div>
      <div class="popup-content" @click.stop>
        <template v-if="isLogin">
          <div class="user-popup">
            <img :src="userAvatar" alt="用户头像" class="popup-avatar">
            <p class="username">{{ userStore.username }}</p>
            <button class="logout-btn" @click="handleLogout">退出登录</button>
          </div>
        </template>
        <LoginAndRegister v-else @close="closePopup" />
      </div>
    </div>
  </transition>
</template>

<script>
import LoginAndRegister from "../Window/LoginAndRegister.vue";
import { useUserStore } from "../../api/user";
import { unref } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'NavigationBar',
  components: { LoginAndRegister },
  props: { itemGap: { type: Number, default: 40 } },
  data() {
    return {
      menuItems: [
        {id: 1, title: '首页', path: '/'},
        {id: 2, title: 'Unity项目', path: '/UnityProject'},
        {id: 3, title: '宣传视频', path: '/PromotionalVideoView'},
        {id: 4, title: '日志', path: '/LogView'},
        {id: 5, title: '刷题工具', path: '/quiz-app-container'},
      ],
      isMenuOpen: false,
      isPopupOpen: false,
      isMounted: false,
      isCollapsed: false, // 新增：控制导航栏收缩状态
    };
  },
  computed: {
    isLogin() {
      return !!this.userStore.isLogin;
    },
    userAvatar() {
      return this.userStore.avatarUrl || "../assets/user-avatar.png";
    },
    userStore() {
      return useUserStore();
    },
    // 修改点3：新增计算属性，判断是否为刷题页面
    isQuizMode() {
      return this.$route.path === '/quiz-app-container';
    }
  },
  mounted() {
    // 监听自定义事件，用于从其他组件控制导航栏
    window.addEventListener('toggle-navbar', this.handleToggleNavbar);
    this.isMounted = true;
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    // 移除事件监听
    window.removeEventListener('toggle-navbar', this.handleToggleNavbar);
    this.isMounted = false;
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    handleAvatarClick() {
      const token = localStorage.getItem('token');
      if (this.isLogin && token) {
        this.$router.push('/user');
        this.closePopup();
      } else {
        this.isPopupOpen = true;
        this.isMenuOpen = false;
        if (this.isLogin && !token) {
          this.userStore.resetState();
        }
      }
    },
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen;
      if (this.isMenuOpen) this.isPopupOpen = false;
    },
    closeMenu() {
      this.isMenuOpen = false;
    },
    togglePopup() {
      this.isPopupOpen = !this.isPopupOpen;
      if (this.isPopupOpen) this.isMenuOpen = false;
    },
    closePopup() {
      this.isPopupOpen = false;
    },
    handleClickOutside(e) {
      if (!this.isMounted) return;
      const currentEl = unref(this.$el);
      // 注意：在刷题模式下，nav元素可能不存在，需要做非空判断
      if (currentEl && !currentEl.contains(e.target) && !this.isQuizMode) {
        this.closeMenu();
        this.closePopup();
      }
    },
    handleLogout() {
      this.userStore.logout();
      this.closePopup();
      this.$message.success('已成功退出登录');
    },
    // 新增：处理返回按钮点击
    handleBack() {
      this.isCollapsed = false; // 展开导航栏
      this.$router.back(); // 回退到上一页
    },
    // 新增：切换导航栏状态的方法
    toggleNavbar(collapsed) {
      this.isCollapsed = collapsed;
    },
    // 新增：处理自定义事件
    handleToggleNavbar(e) {
      if (e && e.detail) {
        this.toggleNavbar(e.detail.collapsed);
      }
    },
    // 修改点4：新增返回首页方法
    goHome() {
      this.$router.push('/');
    }
  },
  setup() {
    return {
      $router: useRouter()
    };
  }
};
</script>

<style scoped>
/* 基础布局样式 */
.navbar {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.nav {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.35);
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 900px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(80, 80, 80, 0.5);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  border-radius: 40px;
  height: 60px;
  transition: all 0.45s cubic-bezier(0.4, 0.15, 0.3, 1);
}

/* PC端用户按钮：右上角 */
.user-btn {
  position: absolute;
  right: 6rem;
  top: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s ease;
  z-index: 1010;
}

.login-text {
  color: #e0e0e0;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 0 8px;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid white;
}

.user-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* 导航链接样式 */
.desktop-nav {
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-link {
  color: rgba(220, 220, 220, 0.9);
  text-decoration: none;
  font-weight: 500;
  font-size: 1.1rem;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
}

.nav-link:hover {
  color: #00ffd0;
  transform: translateY(-2px);
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
}

.nav-link:hover::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  height: 2px;
  background: #4fc3f7;
  border-radius: 2px;
  animation: pulse 1.5s infinite;
}

.router-link-active {
  color: #4fc3f7 !important;
  font-weight: 600;
}

.router-link-active::before {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  height: 3px;
  background: #4fc3f7;
  border-radius: 2px;
}

/* 隐藏汉堡菜单和折叠菜单（不再使用） */
.hamburger, .mobile-nav {
  display: none !important;
}

/* 弹窗样式 */
.popup-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5000;
}

.popup-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 5000;
  transform: scale(0);
  opacity: 0;
  animation: mask-expand 0.35s forwards;
}

.popup-content {
  position: relative;
  z-index: 5010;
  transform: scale(0.8);
  opacity: 0;
  animation: popup-scale 0.35s forwards 0.05s;
}

@keyframes mask-expand {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(0.5);
    opacity: 0.3;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes popup-scale {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.popup-mask.leave-active {
  animation: mask-collapse 0.35s forwards;
}

.popup-content.leave-active {
  animation: popup-scale-reverse 0.35s forwards;
}

@keyframes mask-collapse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0);
    opacity: 0;
  }
}

@keyframes popup-scale-reverse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0.8);
    opacity: 0;
  }
}

/* 用户弹窗内容样式 */
.user-popup {
  background: #1e1e1e;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  width: 280px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}

.popup-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto 15px;
  object-fit: cover;
  border: 3px solid #2d2d2d;
}

.username {
  font-weight: 600;
  margin-bottom: 20px;
  color: #e0e0e0;
}

.logout-btn {
  background: #f56c6c;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.logout-btn:hover {
  background: #e34e4e;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(79, 195, 247, 0.6);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(79, 195, 247, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(79, 195, 247, 0);
  }
}

/* Logo样式（PC端显示/移动端隐藏） */
.title-logo {
  font-family: 'Segoe UI', 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  letter-spacing: -0.05em;
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  display: inline-block;
  text-align: left;
  margin-right: 2rem;
  padding: 0.2em 0;
  transition: all 0.3s ease;
}

.title-logo:hover {
  transform: scale(1.03);
  text-shadow: 0 0 10px rgba(37, 117, 252, 0.3);
}

/* 移动端布局适配（仅修改元素间隔） */
@media (max-width: 768px) {
  /* 1. 移动端隐藏Logo */
  .title-logo {
    display: none;
  }

  /* 2. 导航栏基础样式保持不变，仅调整间距 */
  .nav {
    top: 0;
    left: 0;
    right: 0;
    transform: none;
    width: 100%;
    border-radius: 40px;
  }

  /* 3. 核心修改：缩小导航项之间的间隔 */
  .desktop-nav {
    width: 100%;
    justify-content: center;
    padding: 0 0.5rem; /* 左右预留少量空间，避免贴边 */
  }

  .nav-link {
    /* 覆盖PC端的itemGap，设置移动端紧凑间隔 */
    margin: 0 8px !important;
    font-size: 1rem; /* 保持字体大小，仅缩间距 */
  }

  /* 4. 用户按钮位置保持不变 */
  .user-btn {
    position: fixed;
    bottom: 20px;
    left: 50%;
    top: auto;
    right: auto;
    transform: translateX(-50%);
    width: 50px;
    height: 50px;
  }

  .user-btn:hover {
    transform: translateX(-50%) scale(1.05);
  }
}

/* 小屏移动端微调 */
@media (max-width: 480px) {
  .nav-link {
    font-size: 0.8rem;
    padding: 4px 6px;
  }

  .user-btn {
    width: 45px;
    height: 45px;
    bottom: 15px;
  }
}

/* 新增：返回按钮样式 */
.back-btn {
  position: fixed;
  left: 20px;
  top: 20px;
  z-index: 1010;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  opacity: 1;
  height: 50px;
  transform: translateX(0);
  transition: all 0.35s ease;
  animation: back-btn-fade-in 0.35s ease;
}

@keyframes back-btn-fade-in {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: translateX(2px);
}

/* 新增：导航栏收缩状态样式 */
.nav.collapsed {
  width: auto;
  padding: 0;
  background: transparent;
  box-shadow: none;
  left: 0;
  transform: translateX(-120px) scale(0.6);
  opacity: 0;
  filter: blur(4px);
  transition: all 0.45s cubic-bezier(0.4, 0.15, 0.3, 1);
  height: auto;
}

/* 在收缩状态下隐藏不需要的元素 */
.nav.collapsed .title-logo,
.nav.collapsed .desktop-nav {
  display: none;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .back-btn {
    left: 15px;
    top: 15px;
    padding: 6px 12px;
    font-size: 0.85rem;
  }

  .nav.collapsed {
    transform: translateX(-80px) scale(0.7);
  }
}

/* 导航栏动画：缩放 + 位移 + 模糊 + 渐隐 */
.navbar-anim-enter-active,
.navbar-anim-leave-active {
  transition: all 0.45s cubic-bezier(0.4, 0.15, 0.3, 1);
}

.navbar-anim-enter-from,
.navbar-anim-leave-to {
  transform: translateX(0) scale(1);
  filter: blur(0px);
  opacity: 1;
}

.navbar-anim-enter-to,
.navbar-anim-leave-from {
  transform: translateX(-120px) scale(0.6);
  filter: blur(4px);
  opacity: 0;
}

/* 修改点5：新增刷题页返回按钮样式 */
.quiz-home-btn-container {
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000; /* 必须高于 quiz-app-container 的 100 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.quiz-home-btn {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(10px);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 8px 24px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.quiz-home-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.05);
  border-color: #00ffd0;
  color: #00ffd0;
}
</style>