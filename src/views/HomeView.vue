<template>
  <div class="home-root" @scroll.passive="onScroll">
    <!-- 纯基底背景 -->
    <div class="bg-base"></div>
    
    <!-- 金属泛光背景层 -->
    <div class="metal-glow-container" ref="glowContainer">
      <div class="metal-glow"></div>
    </div>
    
    <!-- 白色线条装饰 -->
    <div class="lines-container">
      <div class="line line-1"></div>
      <div class="line line-2"></div>
      <div class="line line-3"></div>
      <div class="line line-4"></div>
    </div>

    <!-- Hero 区域 -->
    <main class="hero">
      <div class="hero-content">
        <div class="hero-title-container">
          <h1 class="hero-title" ref="titleRef">DigitalMaker</h1>
          <div class="title-line"></div>
        </div>
        <p class="hero-sub">
          Unity3D / UE5 项目外包 · 宣传视频高转化定制
        </p>
        <div class="hero-cta">
          <button class="cta-metal" @click="contact">联系我们</button>
        </div>
      </div>
    </main>

    <!-- 服务区域 -->
    <section class="services">
      <div class="service-item">
        <div class="service-line"></div>
        <h3>专业开发</h3>
        <p>Unity/UE5 全流程开发</p>
      </div>
      <div class="service-item">
        <div class="service-line"></div>
        <h3>视频定制</h3>
        <p>高转化宣传视频制作</p>
      </div>
      <div class="service-item">
        <div class="service-line"></div>
        <h3>满意付款</h3>
        <p>先验收后付款保障</p>
      </div>
    </section>

    <!-- 数据展示 -->
    <section class="stats">
      <div class="stat-item">
        <div class="stat-number" ref="num1">0</div>
        <div class="stat-line"></div>
        <div class="stat-label">完成项目</div>
      </div>
      <div class="stat-item">
        <div class="stat-number" ref="num2">0</div>
        <div class="stat-line"></div>
        <div class="stat-label">客户满意度</div>
      </div>
      <div class="stat-item">
        <div class="stat-number" ref="num3">0</div>
        <div class="stat-line"></div>
        <div class="stat-label">合作保障</div>
      </div>
    </section>

    <!-- 底部区域 -->
    <footer class="footer">
      <div class="footer-line"></div>
      <div class="footer-content">
        <p>专业团队 · 高质量交付</p>
        <button class="footer-btn" @click="contact">联系我们</button>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: "HomeView",
  data() {
    return {
      scrollY: 0,
      mouseX: 0,
      mouseY: 0,
      lastUpdateTime: 0,
    };
  },
  mounted() {
    this.startCountUp();
    window.addEventListener("resize", this.onResize);
    window.addEventListener("scroll", this.onScroll);
    window.addEventListener("mousemove", this.onMouseMove);
    this.initAnimations();
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onResize);
    window.removeEventListener("scroll", this.onScroll);
    window.removeEventListener("mousemove", this.onMouseMove);
    cancelAnimationFrame(this.animationFrameId);
  },
  methods: {
    contact() {
      alert("请接入联系逻辑（微信/QQ/邮箱弹窗）");
    },
    seeCase() {
      alert("跳转到作品页面或展示模态");
    },

    onScroll() {
      this.scrollY = window.scrollY || document.documentElement.scrollTop;
    },

    onMouseMove(e) {
      const now = Date.now();
      if (now - this.lastUpdateTime < 16) return;
      this.lastUpdateTime = now;
      
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
      
      this.updateGlowPosition();
    },

    updateGlowPosition() {
      if (!this.$refs.glowContainer) return;
      
      const glow = this.$refs.glowContainer.querySelector('.metal-glow');
      if (!glow) return;
      
      const x = (this.mouseX / window.innerWidth) * 100;
      const y = (this.mouseY / window.innerHeight) * 100;
      
      glow.style.background = `radial-gradient(circle at ${x}% ${y}%, rgba(255, 255, 255, 0.2) 0%, rgba(200, 220, 255, 0.1) 30%, transparent 60%)`;
      glow.style.transform = `translate(${(x - 50) * 0.8}px, ${(y - 50) * 0.8}px)`;
    },

    /* =============== 动画初始化 =============== */
    initAnimations() {
      // 观察器用于元素进入视口时的动画
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      }, { threshold: 0.1 });
      
      // 观察所有需要动画的元素
      setTimeout(() => {
        document.querySelectorAll('.service-item, .stat-item').forEach(el => {
          observer.observe(el);
        });
      }, 100);
    },

    /* =============== 数字滚动 =============== */
    startCountUp() {
      const easeOut = (t) => 1 - Math.pow(1 - t, 3);
      const run = (el, from, to, duration) => {
        const start = performance.now();
        const tick = (now) => {
          const p = Math.min(1, (now - start) / duration);
          const v = Math.round(from + (to - from) * easeOut(p));
          el.innerText = v + (to >= 100 ? (to === 120 ? "+" : "%") : "");
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      };
      run(this.$refs.num1, 0, 120, 1200);
      run(this.$refs.num2, 0, 99, 1200);
      run(this.$refs.num3, 0, 100, 1200);
    },
  },
};
</script>

<style scoped>
/* ======= 基础样式 ======= */
.home-root {
  position: relative;
  overflow-x: hidden;
  font-family: "Helvetica Neue", "Arial", sans-serif;
  color: #f0f0f0;
  background: #0a0a0a;
  scroll-behavior: smooth;
}

/* ======= 纯基底背景 ======= */
.bg-base {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #0a0a0a;
  z-index: -1;
}

/* ======= 白色线条装饰 ======= */
.lines-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
  pointer-events: none;
}

.line {
  position: absolute;
  background: rgba(255, 255, 255, 0.05);
}

.line-1 {
  top: 15%;
  left: 0;
  width: 100%;
  height: 1px;
}

.line-2 {
  top: 0;
  left: 20%;
  width: 1px;
  height: 100%;
}

.line-3 {
  top: 70%;
  left: 0;
  width: 100%;
  height: 1px;
}

.line-4 {
  top: 0;
  right: 30%;
  width: 1px;
  height: 100%;
}

/* ======= 金属泛光背景层 ======= */
.metal-glow-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.metal-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  transition: background 0.15s ease-out, transform 0.15s ease-out;
  filter: blur(80px);
  background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.2) 0%, rgba(200, 220, 255, 0.1) 30%, transparent 60%);
}

/* ======= Hero 区域 ======= */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  position: relative;
  z-index: 2;
}

.hero-content {
  text-align: center;
  max-width: 800px;
}

.hero-title-container {
  margin-bottom: 40px;
  position: relative;
}

.hero-title {
  font-size: clamp(48px, 8vw, 120px);
  font-weight: 100;
  letter-spacing: -2px;
  color: #ffffff;
  margin: 0;
  line-height: 1;
}

.title-line {
  width: 60px;
  height: 1px;
  background: rgba(255, 255, 255, 0.5);
  margin: 20px auto 0;
}

.hero-sub {
  font-size: 18px;
  font-weight: 300;
  letter-spacing: 1px;
  margin-bottom: 60px;
  opacity: 0.7;
  line-height: 1.6;
}

.hero-cta {
  display: flex;
  justify-content: center;
}

.cta-metal {
  padding: 15px 40px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.5s ease;
}

.cta-metal::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.cta-metal:hover::before {
  left: 100%;
}

.cta-metal:hover {
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

/* ======= 服务区域 ======= */
.services {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1px;
  background: rgba(255, 255, 255, 0.05);
  margin: 100px 0;
  overflow: hidden;
}

.service-item {
  background: #0a0a0a;
  padding: 60px 40px;
  text-align: center;
  position: relative;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}

.service-item.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.service-item:nth-child(1) { transition-delay: 0.1s; }
.service-item:nth-child(2) { transition-delay: 0.2s; }
.service-item:nth-child(3) { transition-delay: 0.3s; }

.service-line {
  width: 40px;
  height: 1px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 auto 30px;
}

.service-item h3 {
  font-size: 18px;
  font-weight: 300;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 15px;
  color: #ffffff;
}

.service-item p {
  font-size: 14px;
  font-weight: 300;
  line-height: 1.6;
  opacity: 0.7;
}

/* ======= 数据展示区域 ======= */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1px;
  background: rgba(255, 255, 255, 0.05);
  margin: 0;
  overflow: hidden;
}

.stat-item {
  background: #0a0a0a;
  padding: 60px 20px;
  text-align: center;
  position: relative;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}

.stat-item.animate-in {
  opacity: 1;
  transform: translateY(0);
}

.stat-item:nth-child(1) { transition-delay: 0.1s; }
.stat-item:nth-child(2) { transition-delay: 0.2s; }
.stat-item:nth-child(3) { transition-delay: 0.3s; }

.stat-number {
  font-size: 64px;
  font-weight: 100;
  color: #ffffff;
  margin-bottom: 20px;
  letter-spacing: -2px;
}

.stat-line {
  width: 30px;
  height: 1px;
  background: rgba(255, 255, 255, 0.3);
  margin: 0 auto 20px;
}

.stat-label {
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  opacity: 0.7;
}

/* ======= 底部区域 ======= */
.footer {
  margin-top: 100px;
  padding: 80px 20px;
  text-align: center;
  position: relative;
}

.footer-line {
  width: 100px;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 auto 40px;
}

.footer-content p {
  font-size: 16px;
  font-weight: 300;
  letter-spacing: 1px;
  margin-bottom: 40px;
  opacity: 0.7;
}

.footer-btn {
  padding: 15px 40px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.5s ease;
}

.footer-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.footer-btn:hover::before {
  left: 100%;
}

.footer-btn:hover {
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
}

/* ======= 移动端适配 ======= */
@media (max-width: 768px) {
  .hero-title {
    font-size: clamp(40px, 10vw, 70px);
  }
  
  .hero-sub {
    font-size: 16px;
    margin-bottom: 40px;
  }
  
  .services {
    grid-template-columns: 1fr;
  }
  
  .service-item {
    padding: 40px 20px;
  }
  
  .stats {
    grid-template-columns: 1fr;
  }
  
  .stat-item {
    padding: 40px 20px;
  }
  
  .stat-number {
    font-size: 48px;
  }
  
  .footer {
    padding: 60px 20px;
  }
}
</style>
