<template>
  <header class="navbar">
    <!-- Logo -->
    <span class="title-logo">DigitalLog</span>

    <!-- 桌面端导航 -->
    <nav class="desktop-nav">
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


    <!-- 用户按钮（最右侧） -->
    <div class="user-btn" @click.stop="handleAvatarClick">
      <span v-if="!isLogin" class="login-text">登录</span>
      <img
          v-else
          :src="userAvatar"
          alt="用户头像"
          class="avatar-img"
      >
    </div>


    <!-- 移动端汉堡菜单 -->
    <div class="hamburger" @click.stop="toggleMenu">
      <div class="hamburger-icon" />
    </div>

    <!-- 移动端折叠菜单 -->
    <transition name="slide-down" appear>
      <nav v-show="isMenuOpen" class="mobile-nav">
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

    <!-- 用户弹窗 -->
    <transition name="fade-in" appear>
      <!-- 修复：明确判断未登录时才显示弹窗容器 -->
      <div v-if="isPopupOpen" class="popup-container">
        <div class="popup-mask" @click="closePopup"></div>
        <div class="popup-content">
          <!-- 登录后显示用户信息 -->
          <template v-if="isLogin">
            <div class="user-popup">
              <img :src="userAvatar" alt="用户头像" class="popup-avatar">
              <p class="username">{{ userStore.username }}</p>
              <button class="logout-btn" @click="handleLogout">退出登录</button>
            </div>
          </template>
          <!-- 未登录显示登录注册（修复：确保此处正确渲染） -->
          <LoginAndRegister v-else @close="closePopup" />
        </div>
      </div>
    </transition>
  </header>
</template>

<script>
import LoginAndRegister from "./Window/LoginAndRegister.vue";
import { useUserStore } from "../api/user";
import { unref } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: 'NavigationBar',
  components: { LoginAndRegister },
  props: { itemGap: { type: Number, default: 40 } },
  data() {
    return {
      menuItems: [
        { id: 1, title: '首页', path: '/' },
        { id: 2, title: 'Working&作品', path: '/about' },
        { id: 3, title: '生活日志', path: '/products' },
        { id: 4, title: '管理', path: '/manage' },
      ],
      isMenuOpen: false,
      isPopupOpen: false, // 控制弹窗显示的核心变量
      isMounted: false,
    };
  },
  computed: {
    // 修复：严格判断登录状态（确保未登录时返回false）
    isLogin() {
      return !!this.userStore.isLogin; // 双重否定确保返回布尔值
    },
    userAvatar() {
      return this.userStore.avatarUrl || "../assets/user-avatar.png";
    },
    userStore() {
      return useUserStore();
    },
  },
  mounted() {
    this.isMounted = true;
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    this.isMounted = false;
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    // 修复：明确未登录时的逻辑
    // 修复登录状态判断逻辑
    handleAvatarClick() {
      // 强制检查本地存储的token来确认登录状态，避免状态管理错误
      const token = localStorage.getItem('token');
      if (this.isLogin && token) {
        // 已登录：跳用户页
        this.$router.push('/user');
        this.closePopup();
      } else {
        // 未登录：显示登录弹窗
        this.isPopupOpen = true;
        this.isMenuOpen = false;

        // 额外保险：重置可能错误的登录状态
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
    // 修复：弹窗显示状态切换
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
      if (currentEl && !currentEl.contains(e.target)) {
        this.closeMenu();
        this.closePopup();
      }
    },
    handleLogout() {
      this.userStore.logout();
      this.closePopup();
      this.$message.success('已成功退出登录');
    },
  },
  setup() {
    return {
      $router: useRouter()
    };
  }
};
</script>


<style scoped>
/* 样式部分保持不变 */
.navbar {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem 2rem;
  background: rgb(255, 255, 255);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  border-radius: 10px;
  height: 60px;
}

.user-btn {
  position: absolute;
  right: 6rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff 0%, #cfe1ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  z-index: 1010;
}

.login-text {
  color: #000000;
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

.desktop-nav {
  display: flex;
  justify-content: center;
  align-items: center;
}

.nav-link {
  color: rgba(0, 0, 0, 0.85);
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

.hamburger {
  display: none;
  position: absolute;
  right: 1.5rem;
  cursor: pointer;
  z-index: 1100;
  padding: 10px;
}

.hamburger-icon {
  width: 30px;
  height: 3px;
  background-color: #000000;
  position: relative;
  transition: all 0.3s ease;
}

.hamburger-icon::before,
.hamburger-icon::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 3px;
  background-color: #000000;
  left: 0;
  transition: all 0.3s ease;
}

.hamburger-icon::before {
  top: -8px;
}

.hamburger-icon::after {
  top: 8px;
}

.mobile-nav {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.62);
  padding: 1rem 0;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
  border-bottom-left-radius: 16px;
  border-bottom-right-radius: 16px;
  backdrop-filter: blur(5px);
  z-index: 1000;
}

.mobile-link {
  display: block;
  color: rgba(0, 0, 0, 0.9);
  text-decoration: none;
  padding: 12px 2rem;
  font-size: 1.1rem;
  transition: all 0.25s ease;
  position: relative;
}

.mobile-link:hover {
  background: rgba(79, 195, 247, 0.15);
  color: #008198;
  padding-left: 2.5rem;
}

.mobile-link::before {
  content: '';
  position: absolute;
  left: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  background: #4fc3f7;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.mobile-link:hover::before {
  opacity: 1;
}

.router-link-active.mobile-link {
  color: #4fc3f7;
  font-weight: 600;
  background: rgba(79, 195, 247, 0.1);
}

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

.user-popup {
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  width: 280px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.popup-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto 15px;
  object-fit: cover;
  border: 3px solid #f0f7ff;
}

.username {
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
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

.title-logo {
  color: black;
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

@media (max-width: 768px) {
  .hamburger {
    display: block;
  }

  .desktop-nav {
    display: none;
  }

  .navbar {
    justify-content: flex-start;
    padding: 0.8rem 1.5rem;
  }

  .user-btn {
    right: 4rem;
    width: 36px;
    height: 36px;
  }

  .popup-container {
    right: 1rem;
    top: 50px;
  }

  .popup-container > .user-popup {
    width: 240px;
  }
}

@media (max-width: 480px) {
  .hamburger {
    right: 1rem;
  }

  .mobile-link {
    padding: 12px 1.5rem;
    font-size: 1rem;
  }

  .user-btn {
    right: 3rem;
  }
}

/* 移动端适配核心修复 */
@media (max-width: 768px) {
  .user-btn {
    position: absolute;
    left: 50%;
    top: 50%;
    /* 基础状态：居中定位（平移） */
    transform: translate(-50%, -50%);
    right: auto;
    width: 36px;
    height: 36px;

    /* 交互状态（hover/active）：同时保留居中平移 + 缩放效果 */
    &:hover,
    &:active {
      transform: translate(-50%, -50%) scale(1.05); /* 关键修复：叠加缩放，不覆盖平移 */
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
  }
}


</style>
