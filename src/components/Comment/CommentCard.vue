<script setup>
import { nextTick, ref, watch } from 'vue';
import { ElMessage as Message } from 'element-plus';
import CommentSonCard from './CommentSonSection.vue';
import { createComment } from '../../api/comment';
import { useUserStore } from '../../api/user';
import userApi from '../../api/user'; // 导入用户API

// 评论输入相关
const commentText = ref('');
const isSubmitting = ref(false);
const userStore = useUserStore();

// 新增：存储评论发布者信息
const commentUser = ref(null);
const isLoadingUser = ref(false);

// eslint-disable-next-line no-undef,no-unused-vars
const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  articleKey: {
    type: String,
    required: true
  }
});

const showReplies = ref(false);
const showReplyInput = ref(false); // 控制回复输入框显示/隐藏

// 通过用户ID获取用户信息
const fetchUserInfo = async (userId) => {
  if (!userId) return;

  try {
    isLoadingUser.value = true;
    const response = await userApi.getUserById(userId);
    const result = response.data;

    // 兼容两种响应格式：{ code: 200, data: ... } 或 { success: true, data: ... }
    if (result.code === 200 || result.success === true) {
      const userData = result.data;
      // 映射后端字段到前端使用的字段
      commentUser.value = {
        id: userData.id,
        name: userData.name,
        avatar: userData.avatarUrl || userData.avatar || '/user-avatar.png', // 优先使用 avatarUrl
        email: userData.email,
        role: userData.role
      };
    } else {
      throw new Error(result.message || '获取用户信息失败');
    }
  } catch (error) {
    console.error('获取评论用户信息失败:', error);
    // 保留原有信息作为 fallback
    commentUser.value = props.comment.user || {
      name: '未知用户',
      avatar: '/user-avatar.png'
    };
  } finally {
    isLoadingUser.value = false;
  }
};

// 监听评论ID变化，重新获取用户信息
watch(
    () => props.comment.userId,
    async () => {
      await fetchUserInfo(props.comment.userId);
    },
    { immediate: true }
);

// 切换子评论显示状态
const toggleReplies = () => {
  showReplies.value = !showReplies.value;
};

// 处理头像加载失败
const handleAvatarError = (event) => {
  event.target.src = '/user-avatar.png';
};

const commentTextareaRef = ref(null);

// 自动调整textarea高度
const autoResizeTextarea = () => {
  nextTick(() => {
    const textarea = commentTextareaRef.value;
    if (!textarea) return;

    // 重置高度以获取正确的scrollHeight
    textarea.style.height = 'auto';
    // 基础高度100px，计算实际需要的高度
    const minHeight = 100;
    const newHeight = Math.max(minHeight, textarea.scrollHeight);
    // 最大高度限制（约4-5行）
    const maxHeight = 200;
    textarea.style.height = Math.min(newHeight, maxHeight) + 'px';

    // 如果内容超过最大高度，显示滚动条
    textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
  });
};

// 提交评论
const handleSubmitComment = async () => {
  const text = commentText.value.trim();
  if (!text) return;
  if (isSubmitting.value) return;

  // 检查用户是否登录
  if (!userStore.isLogin || !userStore.userId) {
    Message.warning('请先登录后再发表回复');
    return;
  }

  // 检查文章ID和评论ID是否存在
  const articleId = props.articleKey;
  const parentId = props.comment.id;
  if (!articleId || !parentId) {
    Message.error('文章ID或评论ID不存在，无法发表回复');
    return;
  }

  try {
    isSubmitting.value = true;

    const commentData = {
      content: text,
      articleId: String(articleId),
      userId: userStore.userId,
      parentId: String(parentId), // 父评论ID
      replyUserId: commentUser.value?.id || props.comment.user?.id || null // 被回复用户ID（回复给顶级评论的作者）
    };

    const result = await createComment(commentData);

    // 处理API响应
    if (result && (result.code === 200 || result.id)) {
      // Message.success('回复发表成功');
      commentText.value = '';
      if (commentTextareaRef.value) {
        commentTextareaRef.value.style.height = '100px';
        commentTextareaRef.value.style.overflowY = 'hidden';
      }
      showReplyInput.value = false;

      // 构造新评论数据（子评论）
      // 优先使用接口返回的数据，否则构造新评论对象
      let newReply;
      if (result.data && result.data.id) {
        // 如果接口返回了完整的评论数据
        newReply = result.data;
        // 确保有 createdAt 字段（兼容 createTime）
        if (!newReply.createdAt && newReply.createTime) {
          newReply.createdAt = newReply.createTime;
        } else if (!newReply.createdAt) {
          newReply.createdAt = new Date().toISOString();
        }
      } else {
        // 否则根据接口返回的ID和当前数据构造新评论对象
        const now = new Date().toISOString();
        newReply = {
          id: result.id || result.data?.id || Date.now().toString(), // 用接口返回ID或临时ID
          content: text,
          userId: userStore.userId,
          articleId: String(articleId),
          parentId: String(parentId),
          replyUserId: commentUser.value?.id || props.comment.user?.id || null,
          createdAt: result.data?.createdAt || result.data?.createTime || now,
          user: {
            id: userStore.userId,
            name: userStore.username || '匿名用户', // userStore 使用 username 字段
            avatarUrl: userStore.avatarUrl || '/user-avatar.png'
          },
          replyToUser: commentUser.value // 被回复用户信息
        };
      }

      // 触发事件时携带新评论数据
      // 先添加临时占位评论触发布局移动
      if (showReplies.value) {
        // 构造临时占位评论（用于触发动画）
        const tempReply = {
          id: 'temp-' + Date.now(),
          content: '',
          userId: userStore.userId,
          articleId: String(articleId),
          parentId: String(parentId),
          replyUserId: commentUser.value?.id || props.comment.user?.id || null,
          createdAt: new Date().toISOString(),
          user: {
            id: userStore.userId,
            name: userStore.username || '匿名用户',
            avatarUrl: userStore.avatarUrl || '/user-avatar.png'
          },
          isTemp: true // 标记为临时占位符
        };
        
        // 先添加临时评论触发布局移动
        window.dispatchEvent(new CustomEvent('reply-submitted', {
          detail: tempReply
        }));
        
        // 短暂延迟后替换为实际评论
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('reply-submitted', {
            detail: newReply
          }));
        }, 50);
      }
      window.dispatchEvent(new CustomEvent('comment-submitted', {
        detail: newReply
      }));
    } else {
      throw new Error(result?.message || '回复发表失败');
    }
  } catch (error) {
    console.error('发表回复失败:', error);
    // 修复错误处理逻辑，增加error存在性检查
    const errorMsg = error
        ? (error.response?.data?.message || error.message || '发表回复失败，请重试')
        : '发表回复失败，请重试';
    Message.error(errorMsg);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div class="comment-card">
    <div class="comment-header">
      <img
          :src="$img(commentUser?.avatar || '/user-avatar.png')"
          alt="用户头像"
          class="avatar"
          @error="handleAvatarError"
          v-if="!isLoadingUser"
      >
      <!-- 加载状态占位 -->
      <div class="avatar-placeholder" v-else></div>

      <div class="user-info">
        <div class="username">
          {{ isLoadingUser ? '加载中...' : commentUser?.name || '未知用户' }}
        </div>
        <div class="date">{{ new Date(comment.createdAt).toLocaleString() }}</div>
      </div>
    </div>
    <div class="comment-content">{{ comment.content }}</div>

    <div class="comment-actions">
      <button class="reply-btn" @click="toggleReplies">
        {{ showReplies ? '收起回复' : '查看回复' }}
      </button>
      <button class="reply-button" @click="showReplyInput = !showReplyInput">
        {{ showReplyInput ? '取消回复' : '回复' }}
      </button>
    </div>

    <!-- 回复输入框：v-if 控制显示，ref 绑定正确 -->
    <div
        class="reply-input-container"
        v-if="showReplyInput"
    >
      <div class="reply-input">
        <div class="reply-input-content">
          <textarea
              ref="commentTextareaRef"
              v-model="commentText"
              class="comment-textarea"
              placeholder="输入你的回复..."
              maxlength="500"
              @keydown.ctrl.enter="handleSubmitComment"
              @keydown.meta.enter="handleSubmitComment"
              @input="autoResizeTextarea"
          ></textarea>
          <button
              class="submit-btn"
              @click="handleSubmitComment"
              :disabled="!commentText.trim() || isSubmitting"
          >
            {{ isSubmitting ? '发送中...' : '发送' }}
          </button>
        </div>

        <div class="reply-input-footer">
          <span class="char-count">{{ commentText.length }}/500</span>
          <span class="shortcut-tip">Ctrl+Enter 快速发送</span>
        </div>
      </div>
    </div>

    <!-- 子评论区 -->
    <CommentSonCard
        v-if="showReplies"
        :parent-id="comment.id"
        :article-key="articleKey"
    />
  </div>
</template>

<style scoped>


/* 基础样式 - 暗黑金属线条风格 */
.comment-card {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0;
  padding: 20px 16px;
  margin-bottom: 16px;
  background-color: #0a0a0a;
  transition: all 0.3s ease;
  box-shadow: none;
}

.comment-card:hover {
  border-color: rgba(255, 255, 255, 0.15);
  background-color: rgba(20, 20, 20, 0.5);
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 0;
  margin-right: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  text-align: left;
  font-weight: 300;
  margin-bottom: 4px;
  color: rgba(255, 255, 255, 0.95);
  font-size: 14px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.date {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 300;
  letter-spacing: 0.3px;
}

.comment-content {
  text-align: left;
  margin-bottom: 12px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  font-weight: 300;
  letter-spacing: 0.3px;
  padding: 0;
}

/* 按钮容器样式 - 实现居中+靠右 */
.comment-actions {
  display: flex;
  width: 100%;
  align-items: center;
  margin-bottom: 16px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* 查看回复按钮 - 居中显示 */
.reply-btn {
  background: transparent;
  border: 1px solid rgba(79, 195, 247, 0.5);
  color: rgba(79, 195, 247, 0.9);
  cursor: pointer;
  padding: 6px 16px;
  font-size: 12px;
  font-weight: 300;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border-radius: 0;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.reply-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(79, 195, 247, 0.3), transparent);
  transition: left 0.5s;
}

.reply-btn:hover::before {
  left: 100%;
}

.reply-btn:hover {
  border-color: rgba(79, 195, 247, 0.8);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(79, 195, 247, 0.3);
}

/* 回复按钮 - 靠卡片最右边 */
.reply-button {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 6px 16px;
  font-size: 12px;
  margin-left: auto;
  transition: all 0.2s;
  font-weight: 300;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border-radius: 0;
}

.reply-button:hover {
  border-color: rgba(255, 255, 255, 0.4);
  color: rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(255, 255, 255, 0.1);
}

/* 评论输入栏主体 */
.reply-input {
  background-color: rgba(20, 20, 20, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0;
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  display: flex;
  height: 100%;
  box-sizing: border-box;
}

.reply-input-content {
  width: 100%;
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

/* 评论输入框 */
.comment-textarea {
  flex: 1;
  min-height: 56px;
  max-height: 150px;
  padding: 12px 14px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0;
  font-size: 14px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  background-color: rgba(20, 20, 20, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  resize: none;
  font-family: inherit;
  box-sizing: border-box;
  transition: all 0.2s ease;
  overflow-y: hidden;
  font-weight: 300;
  letter-spacing: 0.3px;
}

.comment-textarea:focus {
  outline: none;
  border-color: rgba(79, 195, 247, 0.5);
  box-shadow: 0 0 0 1px rgba(79, 195, 247, 0.3);
  background-color: rgba(20, 20, 20, 0.9);
}

.comment-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
  font-size: 13px;
  font-weight: 300;
}

/* 底部信息栏 */
.reply-input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 11px;
}

.char-count {
  color: rgba(255, 255, 255, 0.5);
  font-weight: 300;
  letter-spacing: 0.3px;
}

.shortcut-tip {
  color: rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 300;
  letter-spacing: 0.3px;
}

.shortcut-tip::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 0;
  background-color: rgba(255, 255, 255, 0.5);
}

/* 发送按钮 - 金属风格 */
.submit-btn {
  padding: 8px 20px;
  background: transparent;
  color: rgba(79, 195, 247, 0.9);
  border: 1px solid rgba(79, 195, 247, 0.5);
  border-radius: 0;
  font-size: 13px;
  font-weight: 300;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: none;
  flex-shrink: 0;
  white-space: nowrap;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(79, 195, 247, 0.3), transparent);
  transition: left 0.5s;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn:hover:not(:disabled) {
  border-color: rgba(79, 195, 247, 0.8);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(79, 195, 247, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: none;
}

.submit-btn:disabled {
  background: transparent;
  color: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
  cursor: not-allowed;
  opacity: 0.7;
}

/* 新增加载状态样式 */
.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 0;
  margin-right: 12px;
  background-color: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-color: #1a1a1a;
  }
  50% {
    background-color: #252525;
  }
  100% {
    background-color: #1a1a1a;
  }
}

/* 用于子评论区域的动画容器 */
:deep(.comment-son-section .comments-list) {
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: gap 0.3s ease;
}

:deep(.comment-son-section .new-comment) {
  opacity: 0;
  transform: translateY(-20px);
  animation: fadeIn 0.5s ease-out forwards;
}

:deep(.comment-son-section .existing-comment) {
  transition: transform 0.3s ease-out;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式优化 */
.other-card {
  padding-bottom: 140px !important;
  box-sizing: border-box;
}

@media (max-width: 1024px) {
  .reply-input-container {
    width: 25% !important;
  }
}

@media (max-width: 768px) {
  .comment-card {
    padding: 16px 12px;
    margin-bottom: 12px;
    border-radius: 0;
  }

  .comment-header {
    margin-bottom: 10px;
    padding-bottom: 10px;
  }

  .avatar {
    width: 36px;
    height: 36px;
    margin-right: 10px;
  }

  .username {
    font-size: 13px;
  }

  .date {
    font-size: 10px;
  }

  .comment-content {
    font-size: 13px;
    margin-bottom: 10px;
  }

  .comment-actions {
    margin-bottom: 12px;
    padding-top: 6px;
  }

  .reply-btn {
    padding: 5px 12px;
    font-size: 11px;
  }

  .reply-button {
    padding: 5px 12px;
    font-size: 11px;
  }

  .reply-input-container {
    min-width: 100%;
    right: 0;
    left: 0;
    padding: 8px 12px;
    min-height: 120px;
  }

  .reply-input {
    padding: 14px 16px;
    gap: 10px;
  }

  .comment-textarea {
    font-size: 15px;
    min-height: 60px;
  }

  .submit-btn {
    padding: 9px 24px;
    font-size: 14px;
  }

  .shortcut-tip {
    display: none;
  }
}

@media (max-width: 480px) {
  .comment-card {
    padding: 14px 10px;
    margin-bottom: 10px;
  }

  .comment-header {
    margin-bottom: 8px;
    padding-bottom: 8px;
  }

  .avatar {
    width: 32px;
    height: 32px;
    margin-right: 8px;
  }

  .username {
    font-size: 12px;
  }

  .date {
    font-size: 9px;
  }

  .comment-content {
    font-size: 12px;
    margin-bottom: 8px;
  }

  .comment-actions {
    margin-bottom: 10px;
  }

  .reply-btn {
    padding: 4px 10px;
    font-size: 10px;
  }

  .reply-button {
    padding: 4px 10px;
    font-size: 10px;
  }

  .reply-input-content {
    flex-direction: column;
    align-items: stretch;
  }

  .submit-btn {
    width: 100%;
    padding: 10px;
  }

  .comment-textarea {
    font-size: 16px;
    min-height: 64px;
  }

  .other-card {
    padding-bottom: 160px !important;
  }
}
</style>