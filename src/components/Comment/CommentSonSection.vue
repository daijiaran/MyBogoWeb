<!-- CommentSonSection.vue -->
<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage as Message } from 'element-plus';
import CommentCardSon from './CommentCardSon.vue';
import { getChildComments } from '../../api/comment';

// eslint-disable-next-line no-undef,no-unused-vars
const props = defineProps({
  parentId: {
    type: String,
    required: true
  },
  articleKey: {
    type: String,
    required: true
  }
});

const replies = ref([]);
const isLoading = ref(false);
// 新增状态：标记新评论
const newCommentId = ref('');

// 获取子评论
const fetchReplies = async () => {
  try {
    isLoading.value = true;

    const parentId = props.parentId;
    if (!parentId) {
      console.warn('父评论ID不存在，无法获取子评论');
      replies.value = [];
      return;
    }

    const result = await getChildComments(parentId);

    // 处理API响应（根据实际后端返回格式调整）
    if (result && result.code === 200 && result.data) {
      // 如果返回的是对象包含data字段
      if (Array.isArray(result.data)) {
        replies.value = result.data;
      } else {
        replies.value = [];
      }
    } else if (Array.isArray(result)) {
      // 如果API直接返回数组
      replies.value = result;
    } else {
      replies.value = [];
    }
  } catch (error) {
    console.error('Failed to fetch replies:', error);
    replies.value = [];
    // 修复错误处理逻辑，增加error存在性检查
    const errorMsg = error
        ? (error.response?.data?.message || error.message || '获取回复失败')
        : '获取回复失败';
    Message.error(errorMsg);
  } finally {
    isLoading.value = false;
  }
};

// 刷新子评论列表（当有新回复提交时）
const handleReplySubmitted = (event) => {
  const newComment = event.detail;
  // 验证是否为当前父评论的子评论
  if (newComment && newComment.parentId === props.parentId) {
    // 如果是临时占位符，直接添加
    if (newComment.isTemp) {
      // 检查是否已存在相同的临时占位符
      const existingIndex = replies.value.findIndex(r => r.id === newComment.id);
      if (existingIndex === -1) {
        replies.value.unshift(newComment);
      }
      return;
    }
    
    // 如果是实际评论，检查是否有对应的临时占位符并替换
    const tempIndex = replies.value.findIndex(r => r.isTemp && r.parentId === newComment.parentId);
    if (tempIndex !== -1) {
      // 替换临时占位符
      replies.value[tempIndex] = newComment;
      // 标记新评论ID
      newCommentId.value = newComment.id;
    } else {
      // 没有临时占位符，直接添加
      newCommentId.value = newComment.id;
      replies.value.unshift(newComment);
    }
    
    // 动画结束后清除标记
    setTimeout(() => {
      newCommentId.value = '';
    }, 600);
  } else {
    // 如果不是通过事件传递新评论数据，则重新请求（兼容旧逻辑）
    fetchReplies();
  }
};

onMounted(() => {
  fetchReplies();
  // 监听回复提交事件
  window.addEventListener('reply-submitted', handleReplySubmitted);
});

onUnmounted(() => {
  window.removeEventListener('reply-submitted', handleReplySubmitted);
});
</script>

<template>
  <div class="comment-son-section">
    <div v-if="isLoading">加载回复中...</div>
    <div v-else-if="replies.length === 0" class="no-replies">
      暂无回复
    </div>
    <div v-else class="comments-list">
      <!-- 展示子评论，使用 CommentCardSon 组件 -->
      <CommentCardSon
          v-for="(reply, index) in replies"
          :key="reply.id"
          :comment="reply"
          :article-key="articleKey"
          :class="{
            'new-comment': reply.id === newCommentId,
            'existing-comment': reply.id !== newCommentId && !reply.isTemp,
            'is-temp': reply.isTemp
          }"
          :style="{
            // 为每个评论项添加动态过渡延迟，实现级联效果（临时占位符不应用延迟）
            transitionDelay: (reply.id !== newCommentId && !reply.isTemp) ? `${index * 50}ms` : '0ms'
          }"
      />
    </div>
  </div>
</template>

<style scoped>
/* 基础样式 - 暗黑金属线条风格 */
.comment-son-section {
  margin-top: 16px;
  padding-left: 24px;
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #0a0a0a;
}

/* 新增列表动画样式 */
.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.4s ease-out;
}

/* 优化新评论动画 */
.new-comment {
  opacity: 0;
  transform: translateY(-10px);
  max-height: 0;
  overflow: hidden;
  animation: fadeIn 0.6s ease-out forwards, expandHeight 0.6s ease-out forwards;
}

/* 现有评论过渡效果 */
.existing-comment {
  transition: transform 0.4s ease-out, margin-top 0.4s ease-out;
}

/* 新增展开高度动画 */
@keyframes expandHeight {
  from {
    max-height: 0;
    margin-bottom: 0;
  }
  to {
    max-height: 500px;
    margin-bottom: 12px;
  }
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 原有样式保持不变 */
.no-replies {
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  padding: 8px 0;
  font-weight: 300;
  letter-spacing: 0.3px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .comment-son-section {
    margin-top: 12px;
    padding-left: 16px;
    border-left: 1px solid rgba(255, 255, 255, 0.08);
  }

  .comments-list {
    gap: 10px;
  }

  .no-replies {
    font-size: 13px;
    padding: 6px 0;
  }
}

@media (max-width: 480px) {
  .comment-son-section {
    margin-top: 10px;
    padding-left: 12px;
    border-left: 1px solid rgba(255, 255, 255, 0.06);
  }

  .comments-list {
    gap: 8px;
  }

  .no-replies {
    font-size: 12px;
    padding: 5px 0;
  }
}
</style>