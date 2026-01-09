<template>
  <div ref="cardRef" class="card" :style="cardStyle">
    <!-- skeleton / loading -->
    <div v-if="loading" class="card-skeleton">
      <div class="skeleton-image"></div>
      <div class="skeleton-content">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line medium"></div>
      </div>
    </div>

    <!-- fatal error -->
    <div v-else-if="fatalError" class="card-error">
      <p>{{ fatalError }}</p>
      <button class="retry-btn" @click="retryAll">重试</button>
    </div>

    <!-- 正常显示：图片区+信息区 -->
    <router-link v-else :to="`/article/${article.id}`" class="card-link">
      <div class="card-image-container">
        <img
            v-if="isVisible"
            :src="article.coverUrl || defaultImage"
            :alt="article.title || '封面'"
            class="card-image"
            @error="handleImageError"
            loading="lazy"
        />
        <div v-else class="image-placeholder"></div>
      </div>

      <div class="card-info">
        <h3 class="card-title">{{ article.title || '无标题' }}</h3>

        <div class="card-metadata">
          <div class="metadata-left">
            <div class="channel-info">
              <img v-if="article.publisherAvatar" :src="article.publisherAvatar" alt="avatar" class="avatar" />
              <span class="channel-name">{{ article.publisherName || '未知发布者' }}</span>
            </div>
<!--            <span class="views">{{ formatViews(article.readCount) }} 次观看</span>-->
          </div>

          <span class="upload-time">{{ formatDate(article.createTime) }}</span>
        </div>

        <div v-if="publisherError" class="publisher-error">
          <small class="publisher-error-text">发布者信息加载失败</small>
          <button class="retry-small" @click.prevent="retryFetchPublisher">重试</button>
        </div>
      </div>
    </router-link>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import { useIntersectionLoad } from '../../utils/useIntersectionLoad'
import { getApiBaseUrl } from '../../utils/apiConfig'

axios.defaults.baseURL = getApiBaseUrl()
axios.defaults.withCredentials = true

const articleCache = new Map()
const publisherCache = new Map()

export default {
  name: 'CardArticle',
  props: {
    articleId: { type: [String, Number], required: true },
    width: { type: Number, default: 320 }, // 桌面端默认宽度，手机端自动覆盖
  },
  setup(props) {
    const cardRef = ref(null)
    const loading = ref(true)
    const fatalError = ref('')
    const publisherError = ref('')
    const defaultImage = '/images/default-cover.png'

    const article = reactive({
      id: props.articleId,
      title: '',
      coverUrl: '',
      publisherName: '',
      publisherAvatar: '',
      createTime: '',
      readCount: 0
    })

    // 卡片样式：手机端自动适配宽度
    const cardStyle = computed(() => ({
      '--card-width': `${props.width}px`,
    }))

    // 格式化工具：手机端观看数简化显示（去掉小数）
    const formatDate = (time) => (time ? String(time).split('T')[0] : '刚刚')
    const formatViews = (v) => {
      const n = Number(v) || 0
      if (n >= 10000) return Math.floor(n / 10000) + 'w' // 手机端去掉小数，更简洁
      if (n >= 1000) return Math.floor(n / 1000) + 'k'
      return String(n)
    }

    const handleImageError = (e) => {
      e.target.src = defaultImage
    }

    // 以下保留原有请求、缓存、重试逻辑（无修改）
    const fetchArticle = async () => {
      if (articleCache.has(props.articleId)) {
        Object.assign(article, articleCache.get(props.articleId))
        return
      }

      try {
        const res = await axios.get(`/api/articles/${props.articleId}`)
        if (res?.data?.code === 200 && res.data.data) {
          const data = res.data.data
          article.title = data.title || data.name || ''
          article.coverUrl = data.coverUrl || data.cover || ''
          article.createTime = data.createTime || data.createdAt || ''
          article.readCount = data.readCount || data.read || 0
          articleCache.set(props.articleId, { ...article })
        } else {
          fatalError.value = res?.data?.message || '文章加载失败'
        }
      } catch (err) {
        console.error('[CardArticle] fetchArticle error', err)
        fatalError.value = '网络错误，无法加载文章'
      }
    }

    const fetchPublisher = async () => {
      if (publisherCache.has(props.articleId)) {
        const cached = publisherCache.get(props.articleId)
        article.publisherName = cached.name || article.publisherName
        article.publisherAvatar = cached.avatarUrl || article.publisherAvatar
        publisherError.value = ''
        return
      }

      try {
        const res = await axios.get(`/api/articles/${props.articleId}/publisher`)
        if (res?.data?.code === 200 && res.data.data) {
          article.publisherName = res.data.data.name || article.publisherName || ''
          article.publisherAvatar = res.data.data.avatarUrl || article.publisherAvatar || ''
          publisherCache.set(props.articleId, {
            name: article.publisherName,
            avatarUrl: article.publisherAvatar
          })
          publisherError.value = ''
        } else {
          publisherError.value = res?.data?.message || 'no publisher'
          article.publisherName = article.publisherName || ''
        }
      } catch (err) {
        console.warn('[CardArticle] fetchPublisher failed', err)
        publisherError.value = '网络错误'
      }
    }

    const fetchAll = async () => {
      if (fatalError.value) fatalError.value = ''
      loading.value = true
      await fetchArticle()
      if (fatalError.value) {
        loading.value = false
        return
      }
      await fetchPublisher()
      loading.value = false
    }

    const retryFetchPublisher = async () => {
      publisherError.value = ''
      await fetchPublisher()
    }
    const retryAll = async () => {
      fatalError.value = ''
      loading.value = true
      await fetchAll()
    }

    const { isVisible, forceLoad } = useIntersectionLoad(cardRef, () => {
      fetchAll()
    }, { root: null, rootMargin: '600px', threshold: 0.01, fallbackDelay: 6000 })

    return {
      cardRef,
      article,
      loading,
      fatalError,
      publisherError,
      isVisible,
      defaultImage,
      cardStyle,
      formatDate,
      formatViews,
      handleImageError,
      retryFetchPublisher,
      retryAll,
      forceLoad
    }
  }
}
</script>

<style scoped>
/* 基础样式（桌面端） */
.card {
  width: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: #1e1e1e;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease;
}
.card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}

/* 链接样式 */
.card-link {
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 4:3图片区（核心不变） */
.card-image-container {
  width: 100%;
  padding-bottom: 75%; /* 4:3比例 */
  position: relative;
  background: #2d2d2d;
}
.card-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #2d2d2d;
}

/* 信息区（桌面端） */
.card-info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: #e0e0e0;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-align: left;
}
.card-metadata {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: #999;
  flex-wrap: wrap;
  gap: 8px;
}
.metadata-left {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.channel-info {
  display: flex;
  gap: 6px;
  align-items: center;
}
.channel-name {
  color: #ccc;
}
.avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
}
.views, .upload-time {
  white-space: nowrap;
}

/* 骨架屏、错误状态（桌面端） */
.card-skeleton {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.skeleton-image {
  width: 100%;
  padding-bottom: 75%;
  background: #2d2d2d;
  background-image: linear-gradient(90deg, #2d2d2d 25%, #3a3a3a 37%, #2d2d2d 63%);
  background-size: 400% 100%;
  animation: shimmer 1.2s linear infinite;
}
.skeleton-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skeleton-line {
  height: 12px;
  background: #2d2d2d;
  border-radius: 6px;
  background-image: linear-gradient(90deg, #2d2d2d 25%, #3a3a3a 37%, #2d2d2d 63%);
  background-size: 400% 100%;
  animation: shimmer 1.2s linear infinite;
}
.skeleton-line.short { width: 60%; }
.skeleton-line.medium { width: 80%; }
.skeleton-line.long { width: 100%; }

.card-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #ff6b6b;
  background: #2d1e1e;
  padding: 16px;
  text-align: center;
}
.retry-btn {
  margin-top: 12px;
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid #ff6b6b;
  background: #1e1e1e;
  color: #ff6b6b;
  cursor: pointer;
  transition: all 0.2s;
}
.retry-btn:hover {
  background: #ff6b6b;
  color: #1e1e1e;
}

.publisher-error {
  margin-top: 6px;
  display: flex;
  gap: 8px;
  align-items: center;
}
.publisher-error-text {
  color: #ff6b6b;
  font-size: 12px;
}
.retry-small {
  font-size: 12px;
  border: 1px solid #555;
  padding: 3px 6px;
  border-radius: 4px;
  background: #1e1e1e;
  color: #ccc;
  cursor: pointer;
  transition: all 0.2s;
}
.retry-small:hover {
  border-color: #409eff;
  color: #409eff;
}

@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

/* 🔴 手机端适配（≤768px） */
@media (max-width: 768px) {
  .card {
    width: 100% !important; /* 占满父容器宽度 */
    max-width: 300px; /* 限制最大宽度，避免大屏手机过宽 */
    box-shadow: 0 1px 4px rgba(0,0,0,0.3); /* 弱化阴影，更简洁 */
  }

  /* 图片区：保持4:3，优化圆角 */
  .card-image-container {
    border-radius: 8px 8px 0 0; /* 与卡片圆角呼应 */
  }

  /* 信息区：精简内边距和字体 */
  .card-info {
    padding: 12px;
    gap: 8px;
  }
  .card-title {
    font-size: 0.9rem;
    -webkit-line-clamp: 2; /* 保持2行标题，避免过高 */
    line-height: 1.25;
  }

  /* 元数据：上下布局，避免横向拥挤 */
  .card-metadata {
    font-size: 0.75rem;
    gap: 6px;
    flex-direction: column;
    align-items: flex-start;
  }
  .metadata-left {
    gap: 6px;
    width: 100%;
  }
  .channel-info {
    gap: 4px;
  }
  .avatar {
    width: 18px;
    height: 18px;
  }
  .upload-time {
    font-size: 0.7rem;
    color: #888;
  }

  /* 骨架屏：适配手机端内边距 */
  .skeleton-content {
    padding: 12px;
    gap: 6px;
  }
  .skeleton-line {
    height: 10px;
  }

  /* 错误状态：精简按钮和文字 */
  .card-error {
    padding: 12px;
    font-size: 0.85rem;
  }
  .retry-btn {
    padding: 4px 10px;
    font-size: 0.8rem;
    margin-top: 10px;
  }

  /* 发布者错误：更小字体 */
  .publisher-error-text {
    font-size: 11px;
  }
  .retry-small {
    font-size: 11px;
    padding: 2px 5px;
  }
}

/* 🟡 小屏手机适配（≤480px） */
@media (max-width: 480px) {
  .card-info {
    padding: 10px;
  }
  .card-title {
    font-size: 0.85rem;
  }
  .card-metadata {
    font-size: 0.7rem;
  }
  .views {
    white-space: normal;
    max-width: 60%;
    text-overflow: ellipsis;
    overflow: hidden;
  }
}

</style>