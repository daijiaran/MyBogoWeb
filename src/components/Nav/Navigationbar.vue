<template>
  <transition name="nav-morph">

    <div v-if="!isQuizMode" class="normal-nav-wrapper" key="normal">
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
            <span class="title-logo" v-if="!isCollapsed" @click="handleLogoClick">DigitalMaker</span>

            <nav class="desktop-nav" v-if="!isCollapsed && !isMobile">
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

            <nav class="mobile-mini-nav" v-if="!isCollapsed && isMobile">
              <router-link
                  v-for="item in menuItems.filter(i => [2,3].includes(i.id))"
                  :key="item.id"
                  :to="item.path"
                  class="nav-link mobile-top-link"
              >
                {{ item.title }}
              </router-link>

              <div class="hamburger-icon" @click.stop="openDrawer">
              </div>
            </nav>

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
            :src="$img(userAvatar)"
            alt="用户头像"
            class="avatar-img"
        >
      </div>
    </div>

    <div v-else class="quiz-home-btn-container"  key="quiz" >
      <span class="title-logo" v-if="!isCollapsed " @click="goHome">DigitalMaker</span>
    </div>
  </transition>

  <transition name="fade-in" appear>
    <div v-if="isPopupOpen" class="popup-container">
      <div class="popup-mask" @click="closePopup"></div>
      <div class="popup-content" @click.stop>
        <template v-if="isLogin">
          <div class="user-popup">
            <img :src="$img(userAvatar)" alt="用户头像" class="popup-avatar">
            <p class="username">{{ userStore.username }}</p>
            <button class="logout-btn" @click="handleLogout">退出登录</button>
          </div>
        </template>
        <LoginAndRegister v-else @close="closePopup" />
      </div>
    </div>
  </transition>

  <transition name="drawer-slide">
    <div v-if="isDrawerOpen && isMobile" class="drawer-container">
      <div class="drawer-mask" @click="closeDrawer"></div>
      <div class="mobile-drawer" @click.stop>
        <div class="drawer-header">
          <div class="drawer-user-section" @click="handleAvatarClick">
            <img v-if="isLogin" :src="$img(userAvatar)" alt="用户头像" class="drawer-avatar">
            <span class="drawer-username">{{ isLogin ? userStore.username : '登录' }}</span>
          </div>
          <div class="" @click="closeDrawer">
            <div class="close-icon" />
          </div>
        </div>
        
        <nav class="drawer-nav">
          <router-link
              v-for="item in menuItems"
              :key="item.id"
              :to="item.path"
              class="drawer-nav-link"
              @click="closeDrawer"
          >
            {{ item.title }}
          </router-link>
        </nav>
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
      windowWidth: window.innerWidth,
      isDrawerOpen: false,
      menuItems: [
        { id: 1, title: '首页', path: '/' },
        { id: 2, title: 'Unity项目', path: '/UnityProject' },
        { id: 3, title: '宣传视频', path: '/PromotionalVideoView' },
        { id: 4, title: '日志', path: '/LogView' },
        { id: 5, title: '刷题工具', path: '/quiz-app-container' },
      ],
      isMenuOpen: false,
      isPopupOpen: false,
      isMounted: false,
      isCollapsed: false,
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
    isQuizMode() {
      return this.$route.path === '/quiz-app-container';
    },
    isMobile() {
      return this.windowWidth <= 768;
    }
  },
  mounted() {
    window.addEventListener('toggle-navbar', this.handleToggleNavbar);
    window.addEventListener('resize', this.handleResize);
    this.isMounted = true;
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    window.removeEventListener('toggle-navbar', this.handleToggleNavbar);
    window.removeEventListener('resize', this.handleResize);
    this.isMounted = false;
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    handleAvatarClick() {
      const token = localStorage.getItem('token');
      if (this.isLogin && token) {
        this.$router.push('/user');
        this.closePopup();
        this.closeDrawer();
      } else {
        this.isPopupOpen = true;
        this.isMenuOpen = false;
        this.closeDrawer();
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
    handleBack() {
      this.isCollapsed = false;
      this.$router.back();
    },
    toggleNavbar(collapsed) {
      this.isCollapsed = collapsed;
    },
    handleToggleNavbar(e) {
      if (e && e.detail) {
        this.toggleNavbar(e.detail.collapsed);
      }
    },
    goHome() {
      this.$router.push('/');
    },
    handleResize() {
      this.windowWidth = window.innerWidth;
      if (!this.isMobile) this.isDrawerOpen = false;
    },
    openDrawer() {
      this.isDrawerOpen = true;
      this.isPopupOpen = false;
    },
    closeDrawer() {
      this.isDrawerOpen = false;
    },
    handleLogoClick() {
      if (this.isMobile || this.$route.path !== '/') {
        this.goHome();
      }
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
/* ================= 动画核心代码 ================= */

/* 1. 正常导航包裹层：由于内部 nav 是 fixed，包裹层需要定位以作为动画参照 */
.normal-nav-wrapper {
  position: absolute; /* 在动画期间与按钮重叠 */
  top: 0;
  left: 0;
  width: 100%;
  height: 0; /* 不占据实际高度 */
  z-index: 1500;
  transform-origin: top center; /* 关键：从顶部中心开始缩放 */
}

/* 2. 动画过渡定义 */
.nav-morph-enter-active,
.nav-morph-leave-active {
  /* 使用贝塞尔曲线模拟自然的形变效果 */
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* --- 场景 A: 从正常导航 -> 进入刷题模式 (Nav 收缩) --- */
.nav-morph-leave-to.normal-nav-wrapper {
  /* X轴压缩到0.1（收拢），Y轴微缩，透明度变0 */
  transform: scaleX(0.1) scaleY(0.8);
  opacity: 0;
}

/* --- 场景 A: 此时按钮进入 (Button 展开) --- */
.nav-morph-enter-from.quiz-home-btn-container {
  /* 初始状态：模拟它是从被压缩的状态变出来的 */
  /* 注意：必须保留 translateX(-50%) 否则位置会偏 */
  transform: translateX(-50%) scaleX(0.5) scaleY(0.5);
  opacity: 0;
}

/* --- 场景 B: 从刷题模式 -> 返回正常导航 (Button 收缩) --- */
.nav-morph-leave-to.quiz-home-btn-container {
  transform: translateX(-50%) scaleX(0.5) scaleY(0.5);
  opacity: 0;
}

/* --- 场景 B: 此时导航进入 (Nav 展开) --- */
.nav-morph-enter-from.normal-nav-wrapper {
  transform: scaleX(0.1) scaleY(0.8);
  opacity: 0;
}


/* ================= 以下为原有样式 (保持不变) ================= */

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
  width: 1200px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(80, 80, 80, 0.5);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  border-radius: 40px;
  height: 60px;
  transition: all 0.45s cubic-bezier(0.4, 0.15, 0.3, 1);
}

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

.hamburger, .mobile-nav {
  display: none !important;
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
  backdrop-filter: blur(0px);
  -webkit-backdrop-filter: blur(0px);
  z-index: 5000;
  transform: scale(0);
  opacity: 0;
  transition: backdrop-filter 0.35s ease, -webkit-backdrop-filter 0.35s ease;
  animation: mask-expand 0.35s forwards;
}

.popup-mask.enter-active {
  animation: mask-expand 0.35s forwards, mask-blur-in 0.35s forwards;
}

.popup-mask.leave-active {
  animation: mask-collapse 0.35s forwards, mask-blur-out 0.35s forwards;
}

.popup-content {
  position: relative;
  z-index: 5010;
  transform: scale(0.8);
  opacity: 0;
  animation: popup-scale 0.35s forwards 0.05s;
}

@keyframes mask-expand {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(0.5); opacity: 0.3; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes popup-scale {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.popup-mask.leave-active {
  animation: mask-collapse 0.35s forwards;
}

.popup-content.leave-active {
  animation: popup-scale-reverse 0.35s forwards;
}

@keyframes mask-collapse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0); opacity: 0; }
}

@keyframes mask-blur-in {
  0% { backdrop-filter: blur(0px); -webkit-backdrop-filter: blur(0px); }
  100% { backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); }
}

@keyframes mask-blur-out {
  0% { backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); }
  100% { backdrop-filter: blur(0px); -webkit-backdrop-filter: blur(0px); }
}

@keyframes popup-scale-reverse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(0.8); opacity: 0; }
}

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

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(79, 195, 247, 0.6); }
  70% { box-shadow: 0 0 0 8px rgba(79, 195, 247, 0); }
  100% { box-shadow: 0 0 0 0 rgba(79, 195, 247, 0); }
}

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

@media (max-width: 768px) {
  .nav { top: 0; left: 0; right: 0; transform: none; width: 100%; border-radius: 40px; }
  .desktop-nav { width: 100%; justify-content: center; padding: 0 0.5rem; }
  .nav-link { margin: 0 8px !important; font-size: 1rem; }
  .user-btn { position: fixed; bottom: 20px; left: 50%; top: auto; right: auto; transform: translateX(-50%); width: 50px; height: 50px; }
  .user-btn:hover { transform: translateX(-50%) scale(1.05); }
}

@media (max-width: 480px) {
  .nav-link { font-size: 0.8rem; padding: 4px 6px; }
  .user-btn { width: 45px; height: 45px; bottom: 15px; }
}

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
  from { opacity: 0; transform: translateX(-10px); }
  to { opacity: 1; transform: translateX(0); }
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: translateX(2px);
}

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

.nav.collapsed .title-logo,
.nav.collapsed .desktop-nav { display: none; }

@media (max-width: 768px) {
  .back-btn { left: 15px; top: 15px; padding: 6px 12px; font-size: 0.85rem; }
  .nav.collapsed { transform: translateX(-80px) scale(0.7); }
}

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

.quiz-home-btn-container {
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
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
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.quiz-home-btn:hover {
  background: rgba(0, 0, 0, 0.8);
  transform: scale(1.05);
  border-color: #00ffd0;
  color: #00ffd0;
}

/* ================= 移动端相关样式 ================= */

/* 移动端迷你导航栏 */
.mobile-mini-nav {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 1rem;
}

.mobile-top-link {
  font-size: 0.9rem !important;
  margin: 0 6px !important;
  padding: 6px 10px !important;
}

/* 图标按钮基础样式 */
.icon-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

/* 汉堡菜单按钮 */
.mobile-menu-btn {
  margin-left: auto;
}

.hamburger-icon {
  width: 20px;
  height: 2px;
  background: #e0e0e0;
  position: relative;
  transition: all 0.3s ease;
}

.hamburger-icon::before,
.hamburger-icon::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 2px;
  background: #e0e0e0;
  transition: all 0.3s ease;
}

.hamburger-icon::before {
  top: -6px;
}

.hamburger-icon::after {
  top: 6px;
}

/* 关闭按钮 */
.close-icon {
  width: 20px;
  height: 2px;
  background: #e0e0e0;
  position: relative;
  transform: rotate(45deg);
  transition: all 0.3s ease;
}

.close-icon::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 2px;
  background: #e0e0e0;
  transform: rotate(-90deg);
  transition: all 0.3s ease;
}

/* 侧边抽屉容器 */
.drawer-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 6000;
  display: flex;
  justify-content: flex-end;
}

.drawer-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(0px);
  -webkit-backdrop-filter: blur(0px);
  transition: backdrop-filter 0.35s ease, -webkit-backdrop-filter 0.35s ease;
  animation: mask-expand 0.35s forwards, mask-blur-in 0.35s forwards;
}

.drawer-slide-enter-active .drawer-mask {
  animation: mask-expand 0.35s forwards, mask-blur-in 0.35s forwards;
}

.drawer-slide-leave-active .drawer-mask {
  animation: mask-collapse 0.35s forwards, mask-blur-out 0.35s forwards;
}

.mobile-drawer {
  position: relative;
  width: 85%;
  max-width: 320px;
  height: 100%;
  background: #1a1a1a;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.5);
  animation: drawer-slide-in 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  display: flex;
  flex-direction: column;
}

/* 抽屉头部 */
.drawer-header {
  padding: 2rem 1.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.drawer-user-section:hover {
  transform: translateX(4px);
}

.drawer-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #4fc3f7;
}

.drawer-username {
  color: #e0e0e0;
  font-weight: 500;
  font-size: 1.1rem;
}

/* 抽屉导航菜单 */
.drawer-nav {
  flex: 1;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.drawer-nav-link {
  color: rgba(220, 220, 220, 0.9);
  text-decoration: none;
  font-weight: 500;
  font-size: 1.2rem;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
}

.drawer-nav-link:hover {
  background: rgba(79, 195, 247, 0.1);
  color: #4fc3f7;
  transform: translateX(8px);
}

.drawer-nav-link.router-link-active {
  background: rgba(79, 195, 247, 0.15);
  color: #4fc3f7 !important;
  font-weight: 600;
}

.drawer-nav-link.router-link-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: #4fc3f7;
  border-radius: 0 2px 2px 0;
}

/* 动画效果 */
@keyframes drawer-slide-in {
  0% {
    transform: translateX(100%);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.drawer-slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.drawer-slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .nav {
    padding: 1rem;
  }
  
  .title-logo {
    font-size: 1.2rem !important;
    margin-right: 1rem !important;
  }
  
  .user-btn {
    display: none !important;
  }
}

@media (max-width: 480px) {
  .mobile-mini-nav {
    gap: 8px;
    padding: 0 0.5rem;
  }
  
  .mobile-top-link {
    font-size: 0.8rem !important;
    padding: 4px 8px !important;
  }
  
  .mobile-drawer {
    width: 100%;
  }
  
  .drawer-nav-link {
    font-size: 1.1rem;
    padding: 10px 14px;
  }
}
</style>