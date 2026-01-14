<template>
  <div class="articles-container">
    <!-- 加载中状态 -->
    <div v-if="loading" class="loading-state">
      <p>正在加载您发布的文章...</p>
    </div>

    <!-- 加载错误状态 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchUserArticles">重试</button>
    </div>

    <!-- 加载完成 -->
    <div v-else class="card-grid">
      <!-- 空状态（基于ID数组判断） -->
      <div v-if="filteredArticleIds.length === 0" class="empty-state">
        <p>您暂无已发布的文章</p>
        <button @click="$router.push('/release')">立即发布</button>
      </div>

      <!-- 按ID渲染卡片（核心修改） -->
      <CardArticle
          v-for="id in filteredArticleIds"
          :key="id"
          :article-id="id"
      />
    </div>
  </div>
</template>

<script>
import { onMounted, reactive, toRefs, computed, ref } from 'vue';
import axios from 'axios';
import userApi from "../../api/user";
import { ElMessage } from 'element-plus';
import CardArticle from "./CardArticle.vue";
import { getApiBaseUrl } from '../../utils/apiConfig';

axios.defaults.baseURL = getApiBaseUrl();
axios.defaults.withCredentials = true;

export default {
  name: 'UserArticles',
  components: { CardArticle },
  setup() {
    const state = reactive({
      loading: false,
      error: '',
      userId: null
    });

    // 存储文章ID数组（核心：用于卡片渲染）
    const articleIds = ref([]);

    // 过滤无效ID（同步主页逻辑）
    const filteredArticleIds = computed(() =>
        articleIds.value.filter(id => id !== null && id !== undefined && id !== '')
    );

    // 获取当前用户信息
    const getCurrentUserInfo = async () => {
      try {
        state.loading = true;
        const response = await userApi.getCurrentUser();

        if (response.data.code !== 200) {
          throw new Error(response.data.message || '获取用户信息失败');
        }

        state.userId = response.data.data.id;
      } catch (err) {
        console.error('获取用户信息错误:', err);
        state.error = `获取用户信息失败: ${err.message}`;
        ElMessage.error(state.error);
      } finally {
        state.loading = false;
      }
    };

    // 加载用户文章并提取ID（核心修改）
    const fetchUserArticles = async () => {
      if (!state.userId) {
        state.error = '未获取到用户身份，无法加载文章';
        return;
      }

      state.loading = true;
      state.error = '';
      try {
        const response = await axios.get('/api/articles/filter/by-publisher-uuid', {
          params: {
            page: 0,
            size: 20,
            status: 'PUBLISHED',
            publisherId: state.userId
          }
        });

        if (response.data?.code === 200 && response.data.data) {
          // 从文章列表中提取ID，存入articleIds（关键步骤）
          const articles = Array.isArray(response.data.data.content)
              ? response.data.data.content
              : [];
          articleIds.value = articles.map(article => article.id); // 提取ID数组
        } else {
          state.error = response.data?.message || '获取用户文章失败';
          articleIds.value = []; // 失败时清空ID数组
        }
      } catch (err) {
        console.error('用户文章请求错误:', err);
        state.error = err.response
            ? `状态码: ${err.response.status}，${err.response.data?.message || '服务器错误'}`
            : `网络错误: ${err.message}`;
        articleIds.value = []; // 异常时清空ID数组
      } finally {
        state.loading = false;
      }
    };

    // 挂载时初始化
    onMounted(async () => {
      await getCurrentUserInfo();
      if (state.userId) {
        await fetchUserArticles();
      }
    });

    return {...toRefs(state), filteredArticleIds};
  }
};
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
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  width: 100%;
  max-width: 1400px;
  padding: 16px 0;
  box-sizing: border-box;
  background: black;
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