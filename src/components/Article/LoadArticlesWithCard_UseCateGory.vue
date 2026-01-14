<template>
  <div class="articles-container">
    <!-- 加载中状态 -->
    <div v-if="loading" class="loading-state">
      <p>正在加载文章...</p>
    </div>

    <!-- 加载错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchArticleList">重试</button>
    </div>

    <!-- 加载完成：响应式网格 -->
    <div v-else class="card-grid">
      <CardArticle
          v-for="id in filteredArticleIds"
          :key="id"
          :article-id="id"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import CardArticle from './CardArticle.vue'
import { getApiBaseUrl } from '../../utils/apiConfig'

// 接收父组件传入的categoryId
// eslint-disable-next-line no-undef
const props = defineProps({
  categoryId: {
    type: Number,
    default: 2
  }
})

axios.defaults.baseURL = getApiBaseUrl()
axios.defaults.withCredentials = true

const articleIds = ref([])
const loading = ref(true)
const error = ref('')

const filteredArticleIds = computed(() =>
    articleIds.value.filter(id => id)
)

const fetchArticleList = async () => {
  loading.value = true
  error.value = ''
  try {
    // 修复：使用反引号（`）而不是单引号（'）
    const res = await axios.get(`/api/articles/list/category/${props.categoryId}`)
    if (res.data?.code === 200 && Array.isArray(res.data.data)) {
      articleIds.value = res.data.data.map(item => item.id)
    } else {
      error.value = res.data?.message || '加载失败'
    }
  } catch {
    error.value = '网络错误，请检查连接'
  } finally {
    loading.value = false
  }
}

// 监听categoryId变化，当父组件传入新的categoryId时重新获取数据
watch(() => props.categoryId, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    fetchArticleList()
  }
})

onMounted(fetchArticleList)
</script>

<style scoped>
.articles-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 76px;
  width: 100%;
  box-sizing: border-box;
  background: rgba(0, 0, 0, 0);
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: rgba(240, 240, 240, 0.6);
  width: 100%;
  max-width: 600px;
  font-weight: 300;
  letter-spacing: 1px;
}

.error-state button {
  margin-top: 16px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 10px 20px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-size: 14px;
  position: relative;
  overflow: hidden;
}

.error-state button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.error-state button:hover::before {
  left: 100%;
}

.error-state button:hover {
  border-color: rgba(255, 255, 255, 0.4);
  color: rgba(255, 255, 255, 0.9);
}

/* 网格布局 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 2fr));
  gap: 1px;
  width: 100%;
  max-width: 1400px;
  padding: 16px 0;
  box-sizing: border-box;
  background: rgba(0, 0, 0, 0);
}

/* PC宽屏优化 */
@media (min-width: 1200px) {
  .card-grid {
    padding: 20px 0;
  }
}

/* 平板端 */
@media (max-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    max-width: 900px;
  }
}

/* 手机端（双列） */
@media (max-width: 768px) {
  .articles-container {
    padding: 16px 8px;
  }

  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    padding: 8px 0;
  }

  .loading-state,
  .error-state {
    padding: 40px 15px;
    font-size: 0.9rem;
  }
}

/* 小屏手机（更紧凑） */
@media (max-width: 480px) {
  .card-grid {
    grid-template-columns: repeat(2, minmax(100px, 1fr));
    padding: 6px 4px;
  }
}
</style>