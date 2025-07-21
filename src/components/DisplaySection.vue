<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

// 响应式状态
const images = ref([]) // {url, color}
const currentIndex = ref(0)
const containerBg = ref('#000')
const loading = ref(true)
const error = ref('')
let autoTimer = null

// 获取图片主色调（异步、非阻塞）
const getImageMainColor = (img) => {
  return new Promise((resolve) => {
    requestIdleCallback(() => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d', { willReadFrequently: true })
      const size = 10
      canvas.width = size
      canvas.height = size
      ctx.drawImage(img, 0, 0, size, size)
      const { data } = ctx.getImageData(0, 0, size, size)
      const counts = {}
      let max = 0, main = '#000'
      for (let i = 0; i < data.length; i += 4) {
        const a = data[i + 3]
        if (a < 128) continue
        const hex = `#${((1 << 24) + (data[i] << 16) + (data[i + 1] << 8) + data[i + 2]).toString(16).slice(1)}`
        counts[hex] = (counts[hex] || 0) + 1
        if (counts[hex] > max) { max = counts[hex]; main = hex }
      }
      resolve(main)
    })
  })
}

// 并行预加载
const preloadImage = (url) =>
    new Promise((resolve, reject) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.src = url
      img.onload = async () => {
        const color = await getImageMainColor(img)
        resolve({ url, color })
      }
      img.onerror = () => reject(url)
    })

// 获取封面
const fetchCovers = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/articles', {
      params: { page: 0, size: 10, status: 'PUBLISHED' },
    })
    if (res.data.code !== 200) throw new Error(res.data.msg)
    const list = res.data.data.content
    const coverUrls = list.map(a => a.coverUrl).filter(Boolean).slice(0, 5)

    const result = await Promise.allSettled(coverUrls.map(preloadImage))
    const ok = result.filter(r => r.status === 'fulfilled').map(r => r.value)
    if (ok.length === 0) throw new Error('无有效封面')

    images.value = ok
    containerBg.value = ok[0].color
  } catch (err) {
    console.error(err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 自动播放
const startAuto = () => {
  if (autoTimer || images.value.length <= 1) return
  autoTimer = setInterval(() => {
    next()
  }, 15000)
}

const stopAuto = () => {
  if (autoTimer) clearInterval(autoTimer)
  autoTimer = null
}

// 切换逻辑
const switchTo = (i) => {
  if (i === currentIndex.value) return
  currentIndex.value = i
  containerBg.value = images.value[i].color
}

const next = () => {
  const i = (currentIndex.value + 1) % images.value.length
  switchTo(i)
}

// 生命周期
onMounted(async () => {
  await fetchCovers()
  startAuto()
  // 页面可见性控制
  document.addEventListener('visibilitychange', () => {
    document.hidden ? stopAuto() : startAuto()
  })
})

onBeforeUnmount(stopAuto)
</script>

<template>
  <div class="carousel" :style="{ backgroundColor: containerBg }">
    <div v-if="loading" class="status">加载中...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <template v-else>
      <div class="text-overlay">
        <h1>DigitalLog-DAI</h1>
        <p>分享项目软件开发、游戏开发心得<br>展示 web 开发与 Unity 游戏作品集</p>
      </div>

      <transition-group name="fade" tag="div" class="image-layer">
        <img
            v-for="(img, i) in images"
            v-show="i === currentIndex"
            :key="img.url"
            :src="img.url"
            class="carousel-img"
        />
      </transition-group>

      <div class="indicators">
        <span
            v-for="(img, i) in images"
            :key="i"
            :class="['dot', { active: i === currentIndex }]"
            @click="switchTo(i)"
            @mouseenter="stopAuto"
            @mouseleave="startAuto"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.carousel {
  position: relative;
  width: 100%;
  height: 60vh;
  overflow: hidden;
  border-radius: 10px;
  transition: background-color 0.8s ease;
  will-change: background-color;
}

.carousel-img {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  height: 100%;
  width: auto;
  object-fit: contain;
  will-change: opacity, transform;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.8s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.text-overlay {
  position: absolute;
  top: 60px;
  left: 20px;
  color: #6e6e6e;
  text-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
  z-index: 2;
}

.status {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #595959;
}

.status.error {
  color: #ffcaca;
}

.indicators {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(83, 83, 83, 0.5);
  transition: all 0.3s;
  cursor: pointer;
}

.dot.active {
  width: 28px;
  border-radius: 6px;
  background: #fafafa;
}
</style>
