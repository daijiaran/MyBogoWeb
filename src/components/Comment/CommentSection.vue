<!-- CommentSection.vue -->
<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage as Message } from 'element-plus';
import CommentCard from './CommentCard.vue';
import { getArticleComments } from '../../api/comment';

// eslint-disable-next-line no-undef,no-unused-vars
const props = defineProps({
  articleKey: {
    type: String,
    required: true
  }
});

const comments = ref([]);
const isLoading = ref(true);
const currentPage = ref(0);
const pageSize = ref(10);
const hasMore = ref(true);
// 新增状态：控制新评论的动画
const newCommentId = ref(''); // 标记最新添加的评论ID

// 从后端获取评论
const fetchComments = async (page = 0) => {
  try {
    if (page === 0) {
      isLoading.value = true;
    }

    const articleId = props.articleKey;
    if (!articleId) {
      console.warn('文章ID不存在，无法获取评论');
      comments.value = [];
      return;
    }

    const result = await getArticleComments(articleId, page, pageSize.value);

    // 处理API响应（根据实际后端返回格式调整）
    let commentList = [];
    if (result && result.code === 200 && result.data) {
      // 如果返回的是分页对象
      if (result.data.content) {
        commentList = result.data.content;
        hasMore.value = !result.data.last; // 是否还有下一页
      } else if (Array.isArray(result.data)) {
        // 如果直接返回数组
        commentList = result.data;
        hasMore.value = commentList.length >= pageSize.value;
      } else if (Array.isArray(result)) {
        // 如果直接返回数组（没有包装）
        commentList = result;
        hasMore.value = commentList.length >= pageSize.value;
      }
    } else if (Array.isArray(result)) {
      // 如果API直接返回数组
      commentList = result;
      hasMore.value = commentList.length >= pageSize.value;
    }

    // 过滤出顶级评论（没有parentId的评论）
    const topLevelComments = commentList.filter((comment) => !comment.parentId);

    if (page === 0) {
      comments.value = topLevelComments;
    } else {
      comments.value = [...comments.value, ...topLevelComments];
    }

    currentPage.value = page;
  } catch (error) {
    console.error('Failed to fetch comments:', error);
    comments.value = [];
    // 修复错误处理逻辑，增加error存在性检查
    const errorMsg = error
        ? (error.response?.data?.message || error.message || '获取评论失败')
        : '获取评论失败';
    Message.error(errorMsg);
  } finally {
    isLoading.value = false;
  }
};

// 刷新评论列表（当有新评论提交时）
const handleCommentSubmitted = (event) => {
  const newComment = event.detail;
  // 验证是否为有效的顶级评论
  if (newComment && !newComment.parentId) {
    // 标记新评论ID（用于触发动画）
    newCommentId.value = newComment.id;
    // 将新评论添加到列表头部
    comments.value.unshift(newComment);
    // 动画结束后清除标记（可选）
    setTimeout(() => {
      newCommentId.value = '';
    }, 500);
  } else {
    // 如果不是通过事件传递新评论数据，则重新请求（兼容旧逻辑）
    fetchComments(0);
  }
};

onMounted(() => {
  fetchComments(0);
  // 监听评论提交事件
  window.addEventListener('comment-submitted-root', handleCommentSubmitted);
});

onUnmounted(() => {
  window.removeEventListener('comment-submitted', handleCommentSubmitted);
});
</script>

<template>
  <div class="comment-section">
    <h3>评论区</h3>
    <div v-if="isLoading" class="loading">加载中...</div>
    <div v-else-if="comments.length === 0" class="no-comments">暂无评论</div>
    <div v-else class="comments-list">
      <CommentCard
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          :article-key="articleKey"
          :class="{
            'new-comment': comment.id === newCommentId,
            'existing-comment': comment.id !== newCommentId
          }"
      />
    </div>
  </div>
</template>

<style scoped>
/* 基础样式 - 暗黑金属线条风格 */
.comment-section {
  width: 100%;
  box-sizing: border-box;
  background-color: #0a0a0a;
}

.comment-section h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 300;
  color: rgba(255, 255, 255, 0.95);
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 12px;
}

.loading, .no-comments {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 0.3px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: gap 0.3s ease;
}

/* 现有评论的下移动画 */
.existing-comment {
  transition: transform 0.3s ease-out;
}

/* 新评论的渐显动画 */
.new-comment {
  opacity: 0;
  transform: translateY(-20px);
  animation: fadeIn 0.5s ease-out forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式优化 */
@media (max-width: 768px) {
  .comment-section h3 {
    font-size: 16px;
    margin-bottom: 16px;
    padding-bottom: 10px;
  }

  .loading, .no-comments {
    padding: 30px 15px;
    font-size: 13px;
  }

  .comments-list {
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .comment-section h3 {
    font-size: 15px;
    margin-bottom: 14px;
    padding-bottom: 8px;
  }

  .loading, .no-comments {
    padding: 25px 12px;
    font-size: 12px;
  }

  .comments-list {
    gap: 10px;
  }
}
</style>