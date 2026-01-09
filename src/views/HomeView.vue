<template>
  <div class="home-root" @scroll.passive="onScroll">
    <canvas ref="bgCanvas" class="bg-canvas"></canvas>
    <div class="bg-overlay"></div>

    <!-- Hero -->
    <main class="hero" @mousemove="onPointerMove" @touchmove="onTouchMove">
      <h1 class="hero-title" ref="titleRef">DigitalMaker</h1>
      <p class="hero-sub">
        Unity3D / UE5 项目外包 · 宣传视频高转化定制
      </p>
      <div class="hero-cta"></div>
    </main>

<!--    &lt;!&ndash; 服务卡片 &ndash;&gt;-->
<!--    <section class="services">-->
<!--      <article class="card" v-parallax>-->
<!--        <h3 style="color: white;">Unity / UE 开发外包</h3>-->
<!--        <p>-->
<!--          500+ 项目经验 · 专业团队全流程承接 · AR/VR/仿真/游戏开发外包 ·-->
<!--          满意再付款-->
<!--        </p>-->
<!--        <div class="card-actions">-->
<!--          <button class="btn neon">查看案例</button>-->
<!--        </div>-->
<!--      </article>-->

<!--      <article class="card" v-parallax>-->
<!--        <h3 style="color: white;">宣传视频制作</h3>-->
<!--        <p>-->
<!--          Minecraft / 游戏服务器宣传 · 平均播放 4000+ · 新服推广首选 ·-->
<!--          转化率高 · 价格灵活-->
<!--        </p>-->
<!--        <div class="card-actions">-->
<!--          <button class="btn neon alt">了解更多</button>-->
<!--        </div>-->
<!--      </article>-->
<!--    </section>-->

    <!-- 实力展示 -->
    <section class="stats">
      <div class="stat">
        <div class="stat-num" ref="num1">0</div>
        <div class="stat-label">完成项目</div>
      </div>
      <div class="stat">
        <div class="stat-num" ref="num2">0</div>
        <div class="stat-label">客户满意度</div>
      </div>
      <div class="stat">
        <div class="stat-num" ref="num3">0</div>
        <div class="stat-label">满意后付款</div>
      </div>
    </section>

    <footer class="footer">
      <div>想了解项目报价或合作细节？立即联系我们！</div>
      <div class="contact-btns">
        <button class="btn contact">微信 / QQ / 邮箱咨询</button>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: "HomeView",
  directives: {
    parallax: {
      mounted(el) {
        // ⭐ 移动端禁用，提高性能
        if (window.innerWidth <= 768) return;

        el.addEventListener("mousemove", (e) => {
          const r = el.getBoundingClientRect();
          const cx = r.left + r.width / 2;
          const cy = r.top + r.height / 2;
          const dx = (e.clientX - cx) / r.width;
          const dy = (e.clientY - cy) / r.height;
          el.style.transform = `translate(${dx * 8}px, ${dy * 8}px) scale(1.02)`;
        });
        el.addEventListener("mouseleave", () => {
          el.style.transform = "translate(0,0) scale(1)";
        });
      },
    },
  },
  data() {
    return {
      pointer: { x: 0, y: 0 },
      scrollY: 0,
    };
  },
  mounted() {
    this.initCanvas();
    this.startCountUp();

    // ⭐ PC 才启用 title 位移
    if (window.innerWidth > 768) {
      window.addEventListener("mousemove", this.onWindowMove);
    }

    window.addEventListener("resize", this.onResize);
    window.addEventListener("scroll", this.onScroll);
  },
  beforeUnmount() {
    window.removeEventListener("mousemove", this.onWindowMove);
    window.removeEventListener("resize", this.onResize);
    window.removeEventListener("scroll", this.onScroll);
    cancelAnimationFrame(this.bgRAF);
  },
  methods: {
    contact() {
      alert("请接入联系逻辑（微信/QQ/邮箱弹窗）");
    },
    seeCase() {
      alert("跳转到作品页面或展示模态");
    },

    onPointerMove(e) {
      this.pointer.x = e.clientX;
      this.pointer.y = e.clientY;
    },
    onTouchMove(e) {
      const t = e.touches[0];
      this.pointer.x = t.clientX;
      this.pointer.y = t.clientY;
    },

    onScroll() {
      this.scrollY = window.scrollY || document.documentElement.scrollTop;
    },

    onWindowMove(e) {
      const title = this.$refs.titleRef;
      if (!title) return;
      const cx = window.innerWidth / 2;
      const dx = (e.clientX - cx) / cx;
      title.style.transform = `translateX(${dx * 8}px) translateZ(0)`;
    },

    onResize() {
      if (!this.canvas) return;
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    },

    /* =============== 背景 Canvas =============== */
    initCanvas() {
      this.canvas = this.$refs.bgCanvas;
      this.ctx = this.canvas.getContext("2d");
      this.canvas.width = window.innerWidth * 0.9; // ⭐ 降低分辨率提升性能
      this.canvas.height = window.innerHeight * 0.9;

      // ⭐ 移动端粒子减少，性能提升
      const blobCount = window.innerWidth < 768 ? 6 : 12;

      const colors = [
        { h: 200, s: 90, l: 60 },
        { h: 270, s: 85, l: 60 },
        { h: 320, s: 85, l: 60 },
        { h: 150, s: 80, l: 55 },
      ];

      this.blobs = [];
      for (let i = 0; i < blobCount; i++) {
        const c = colors[i % colors.length];
        this.blobs.push({
          x: Math.random() * innerWidth,
          y: Math.random() * innerHeight,
          vx: (Math.random() - 0.5) * 0.6,
          vy: (Math.random() - 0.5) * 0.6,
          r: 100 + Math.random() * 220,
          color: c,
          life: Math.random() * 1000,
        });
      }

      this.animate();
    },

    animate() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;

      ctx.clearRect(0, 0, w, h);
      ctx.globalCompositeOperation = "lighter";

      for (let i = 0; i < this.blobs.length; i++) {
        const b = this.blobs[i];
        b.x += b.vx * 1.5;
        b.y += b.vy * 1.5;

        const scrollEffect = this.scrollY * 0.001;
        b.y += Math.sin(scrollEffect + i) * 0.6;

        if (b.x < -b.r) b.x = w + b.r;
        if (b.x > w + b.r) b.x = -b.r;
        if (b.y < -b.r) b.y = h + b.r;
        if (b.y > h + b.r) b.y = -b.r;

        const hue = (b.color.h + b.life / 10) % 360;
        const gradient = ctx.createRadialGradient(b.x, b.y, 0, b.x, b.y, b.r);
        gradient.addColorStop(0, `hsla(${hue}, ${b.color.s}%, ${b.color.l}%, 0.3)`);
        gradient.addColorStop(1, `hsla(${(hue + 40) % 360}, ${b.color.s}%, ${b.color.l}%, 0.05)`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
        ctx.fill();
        b.life += 1;
      }

      ctx.globalCompositeOperation = "overlay";
      ctx.fillStyle = "rgba(10, 10, 20, 0.12)";
      ctx.fillRect(0, 0, w, h);

      this.bgRAF = requestAnimationFrame(() => this.animate());
    },

    /* =============== 数字滚动 =============== */
    startCountUp() {
      const easeOut = (t) => 1 - Math.pow(1 - t, 3);
      const run = (el, from, to, duration) => {
        const start = performance.now();
        const tick = (now) => {
          const p = Math.min(1, (now - start) / duration);
          const v = Math.round(from + (to - from) * easeOut(p));
          el.innerText = v + (to >= 100 ? (to === 500 ? "+" : "%") : "");
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      };
      run(this.$refs.num1, 0, 500, 1200);
      run(this.$refs.num2, 0, 99, 1200);
      run(this.$refs.num3, 0, 100, 1200);
    },
  },
};
</script>

<style scoped>
/* ======= 主体视觉 ======= */
.home-root {
  position: relative;
  overflow-x: hidden;
  font-family: "Inter", "Poppins", sans-serif;
  color: #eaf0ff;
  background: #050508;
  scroll-behavior: smooth;
}

/* ======= 背景效果 ======= */
.bg-canvas {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  filter: blur(20px) saturate(130%) brightness(1.1);
  pointer-events: none;
}
.bg-overlay {
  position: fixed;
  inset: 0;
  z-index: 1;
  background: radial-gradient(circle at 30% 40%, rgba(60, 80, 200, 0.2), transparent 70%),
  radial-gradient(circle at 70% 70%, rgba(220, 60, 180, 0.15), transparent 70%);
  mix-blend-mode: overlay;
  pointer-events: none;
}

/* ======= Hero ======= */
.hero {
  min-height: 80vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 10;
  text-align: center;
  padding: 120px 20px 60px;
}
.hero-title {
  font-size: clamp(48px, 7vw, 96px);
  font-weight: 800;
  background: linear-gradient(90deg, #8defff, #a78bfa, #ff77e0);
  -webkit-background-clip: text;
  color: transparent;
  animation: floatTitle 6s ease-in-out infinite;
}
@keyframes floatTitle {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}
.hero-sub {
  margin-top: 18px;
  font-size: 18px;
  opacity: 0.85;
}

/* ======= 服务卡片 ======= */
.services {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 32px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
}
.card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  padding: 28px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5);
  transition: all 0.3s ease;
}
.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 50px rgba(100, 100, 255, 0.3);
}

/* ======= 实力展示 - 移动端适配 ======= */
.stats {
  margin: 60px auto;
  display: flex;
  justify-content: center;
  gap: 60px;
}

/* ⭐ 移动端垂直展示，不挤压 */
@media (max-width: 768px) {
  .stats {
    flex-direction: column;
    align-items: center;
    gap: 32px;
  }
}

.stat-num {
  font-size: 64px;
  font-weight: 800;
  color: #eaf0ff;
  text-shadow: 0 4px 20px rgba(60, 100, 200, 0.3);
}
.stat-label {
  font-size: 14px;
  opacity: 0.8;
}

/* ======= 底部 ======= */
.footer {
  text-align: center;
  margin-bottom: 100px;
  color: rgba(220, 230, 255, 0.8);
}
.card-actions,
.contact-btns {
  color: #1d2129;
}
</style>
