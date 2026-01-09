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
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import CardArticle from './CardArticle.vue'
import { getApiBaseUrl } from '../../utils/apiConfig'

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
    const res = await axios.get('/api/articles/list')
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

onMounted(fetchArticleList)
</script>

<style scoped>
.articles-container {

  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  width: 100%;
  box-sizing: border-box;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  width: 100%;
  max-width: 600px;
}

.error-state button {
  margin-top: 16px;
  border: 1px solid #d33;
  background: none;
  padding: 8px 16px;
  color: #d33;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.error-state button:hover {
  background: #d33;
  color: #fff;
  transform: translateY(-2px);
}

/* 🟢 网格布局 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 2fr));
  gap: 24px;
  width: 100%;
  max-width: 1400px;
  padding: 16px 0;
  box-sizing: border-box;
}

/* PC宽屏优化 */
@media (min-width: 1200px) {
  .card-grid {
    gap: 30px;
    padding: 20px 0;
  }
}

/* 平板端 */
@media (max-width: 1024px) {
  .card-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 18px;
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
    gap: 12px;
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
    gap: 10px;
    padding: 6px 4px;
  }
}
</style>
