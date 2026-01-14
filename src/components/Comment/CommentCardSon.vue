<!-- CommentCardSon.vue - 子评论展示组件 -->
<script setup>
import { nextTick, ref, watch } from 'vue';
import { ElMessage as Message } from 'element-plus';
import { createComment } from '../../api/comment';
import { useUserStore } from '../../api/user';
import userApi from '../../api/user'; // 导入用户API

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

// 评论输入相关
const commentText = ref('');
const isSubmitting = ref(false);
const showReplyInput = ref(false); // 控制回复输入框显示/隐藏
const userStore = useUserStore();

// 新增：存储评论发布者信息
const commentUser = ref(null);
const isLoadingUser = ref(false);

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

// 处理头像加载失败
const handleAvatarError = (event) => {
  event.target.src = '/user-avatar.png';
};

// 获取回复目标用户（支持多种字段名）
const getReplyToUser = () => {
  return props.comment.replyToUser || props.comment.replyTo || props.comment.targetUser || null;
};

const commentTextareaRef = ref(null);

// 自动调整textarea高度
const autoResizeTextarea = () => {
  nextTick(() => {
    const textarea = commentTextareaRef.value;
    if (!textarea) return;

    // 重置高度以获取正确的scrollHeight
    textarea.style.height = 'auto';
    // 基础高度56px（最小），计算实际需要的高度
    const minHeight = 56;
    const newHeight = Math.max(minHeight, textarea.scrollHeight);
    // 最大高度限制（约4-5行）
    const maxHeight = 150;
    textarea.style.height = Math.min(newHeight, maxHeight) + 'px';

    // 如果内容超过最大高度，显示滚动条
    if (textarea.scrollHeight > maxHeight) {
      textarea.style.overflowY = 'auto';
    } else {
      textarea.style.overflowY = 'hidden';
    }
  });
};

// 提交回复
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
  const parentId = props.comment.parentId || props.comment.id; // 使用parentId或当前评论的id作为父评论ID
  if (!articleId || !parentId) {
    Message.error('文章ID或评论ID不存在，无法发表回复');
    return;
  }

  try {
    isSubmitting.value = true;

    // 获取被回复的用户ID（回复给当前评论的作者）
    const replyUserId = commentUser.value?.id || props.comment.user?.id || null;

    const commentData = {
      content: `@${commentUser.value?.name || '未知用户'} ${text}`,
      articleId: String(articleId),
      userId: userStore.userId,
      parentId: String(parentId), // 父评论ID（子评论的parentId）
      replyUserId: replyUserId // 被回复用户ID（回复给当前评论的作者）
    };

    const result = await createComment(commentData);

    // 处理API响应
    if (result && (result.code === 200 || result.id)) {
      // Message.success('回复发表成功');
      commentText.value = '';
      if (commentTextareaRef.value) {
        commentTextareaRef.value.style.height = '56px';
        commentTextareaRef.value.style.overflowY = 'hidden';
      }
      showReplyInput.value = false;

      // 构造新评论数据（嵌套子评论）
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
        // 确保内容包含@用户名（如果接口返回的没有）
        if (newReply.content && !newReply.content.includes('@') && commentUser.value?.name) {
          newReply.content = `@${commentUser.value.name} ${newReply.content}`;
        }
      } else {
        // 否则根据接口返回的ID和当前数据构造新评论对象
        const now = new Date().toISOString();
        newReply = {
          id: result.id || result.data?.id || Date.now().toString(),
          content: `@${commentUser.value?.name || '未知用户'} ${text}`,
          userId: userStore.userId,
          articleId: String(articleId),
          parentId: String(parentId),
          replyUserId: replyUserId,
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
      // 构造临时占位评论（用于触发动画）
      const tempReply = {
        id: 'temp-' + Date.now(),
        content: '',
        userId: userStore.userId,
        articleId: String(articleId),
        parentId: String(parentId),
        replyUserId: replyUserId,
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

// 拆分评论内容中的@用户部分，给@用户添加蓝色样式类
const formatCommentContent = (content) => {
  if (!content) return '';
  // 正则匹配开头的 "@用户名 " 格式（@+非空格字符+空格）
  const atReg = /^(@\S+)\s+/;
  const match = content.match(atReg);
  if (match) {
    const atPart = match[1]; // @用户名
    const restContent = content.slice(atPart.length + 1); // 剩余回复内容
    return `<span class="at-user">${atPart}</span> ${restContent}`;
  }
  return content; // 无@用户时返回原内容
};


</script>

<template>
  <div class="comment-card-son" :class="{ 'is-temp': comment.isTemp }">
    <div v-if="!comment.isTemp">
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


      <div class="comment-content">
        <!-- 只保留一次"回复目标用户"的@显示 -->
        <span v-if="getReplyToUser()" class="reply-to">
      @{{ getReplyToUser().name }}
    </span>
        <!-- 直接渲染处理后的评论内容（带@用户蓝色样式） -->
        <span v-html="formatCommentContent(comment.content)"></span>
      </div>
    </div>
    
    
    
    <div v-if="!comment.isTemp" class="comment-actions">
      <button class="reply-button" @click="showReplyInput = !showReplyInput">
        {{ showReplyInput ? '取消回复' : '回复' }}
      </button>
    </div>

    <!-- 回复输入框：v-if 控制显示，ref 绑定正确 -->
    <div
        class="reply-input-container"
        v-if="showReplyInput && !comment.isTemp"
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
  </div>
</template>

<style scoped>
/* 基础样式 - 暗黑金属线条风格 */
.comment-card-son {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0;
  padding: 16px 14px;
  margin-bottom: 12px;
  background-color: rgba(20, 20, 20, 0.5);
  transition: all 0.3s ease;
  min-height: 80px;
  box-sizing: border-box;
}

.comment-card-son:hover {
  border-color: rgba(255, 255, 255, 0.12);
  background-color: rgba(30, 30, 30, 0.6);
}

/* 添加临时占位符样式 */
.comment-card-son.is-temp {
  border: none;
  background-color: transparent;
  padding: 0;
  margin-bottom: 0;
  min-height: 80px;
  overflow: hidden;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 0;
  margin-right: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 300;
  font-size: 13px;
  margin-bottom: 2px;
  color: rgba(255, 255, 255, 0.9);
  text-align: left;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.date {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.4);
  font-weight: 300;
  letter-spacing: 0.3px;
}

.comment-content {
  text-align: left;
  line-height: 1.6;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  padding-left: 0;
  margin-bottom: 8px;
  font-weight: 300;
  letter-spacing: 0.3px;
}

.reply-to {
  color: rgba(79, 195, 247, 0.9);
  font-weight: 300;
  margin-right: 4px;
  cursor: pointer;
  letter-spacing: 0.3px;
}

.reply-to:hover {
  text-decoration: underline;
}

/* 按钮容器样式 - 靠右显示 */
.comment-actions {
  display: flex;
  width: 100%;
  align-items: center;
  margin-bottom: 8px;
  padding-left: 0;
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

/* 回复按钮 - 靠右显示 */
.reply-button {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 5px 14px;
  font-size: 11px;
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

/* 评论输入栏容器 */
.reply-input-container {
  margin-top: 0px;
  padding-left: 0;
  width: 100%;
  box-sizing: border-box;
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
  width: 36px;
  height: 36px;
  border-radius: 0;
  margin-right: 10px;
  background-color: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: loading 1.5s infinite;
  flex-shrink: 0;
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

/* @用户 蓝色样式（与现有.reply-to风格一致） */
.at-user {
  color: rgba(79, 195, 247, 0.9);
  font-weight: 300;
  cursor: pointer;
  letter-spacing: 0.3px;
}

.at-user:hover {
  text-decoration: underline;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .comment-card-son {
    padding: 14px 12px;
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
    margin-bottom: 6px;
  }

  .comment-actions {
    margin-bottom: 6px;
    padding-top: 4px;
  }

  .reply-button {
    padding: 4px 12px;
    font-size: 10px;
  }

  .reply-input-container {
    padding-left: 0;
  }

  .reply-input {
    padding: 12px 14px;
    gap: 8px;
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
  .comment-card-son {
    padding: 12px 10px;
    margin-bottom: 8px;
  }

  .comment-header {
    margin-bottom: 6px;
    padding-bottom: 6px;
  }

  .avatar {
    width: 30px;
    height: 30px;
    margin-right: 6px;
  }

  .username {
    font-size: 11px;
  }

  .date {
    font-size: 9px;
  }

  .comment-content {
    font-size: 11px;
    margin-bottom: 6px;
  }

  .comment-actions {
    margin-bottom: 6px;
  }

  .reply-button {
    padding: 4px 10px;
    font-size: 9px;
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
}

</style>