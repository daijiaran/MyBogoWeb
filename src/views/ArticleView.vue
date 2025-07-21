<template>
  <div class="article-view">
    <div class="container">
      <!-- 左侧浏览区 - 添加ref和缩放样式 -->
      <div
          class="left-panel"
          :style="{ width: leftPanelWidth + '%' }"
          ref="leftPanelRef"
      >
        <div class="markdown-view">
          <!-- 缩放容器：只对该容器内内容缩放 -->
          <div
              class="content-wrapper"
              :style="{
                transform: `scale(${scaleRatio})`,
                transformOrigin: 'top center',
                transition: 'transform 0.2s ease',
                // 保持布局稳定，缩放不影响外层滚动
                display: 'inline-block',
                width: '100%',
                boxSizing: 'border-box'
              }"
          >
            <h1 class="main-title">{{ article.title }}</h1>
            <p class="intro-text">
              {{ article.summary }}
            </p>

            <div class="divider"></div>
            <mark-down-reader :content="article.content"></mark-down-reader>
          </div>
        </div>
      </div>

      <!-- 分隔线 -->
      <div
          class="resizer"
          @mousedown="startDrag"
          :class="{ 'resizing': isDragging }"
      >
        <div class="resizer-dot"></div>
      </div>

      <!-- 右侧信息区 -->
      <div
          class="right-panel"
          :style="{
            width: rightPanelWidth + '%',
            '--right-panel-width-value': rightPanelWidth + '%'
          }"
      >
        <div class="info-container">
          <!-- 封面区域 -->
          <div class="cover-card">
            <img
                :src="article.coverUrl ? `http://localhost:8080${article.coverUrl}` : ''"
                class="cover-image"
                v-if="article.coverUrl"
                :alt="article.title"
            />
            <div class="cover-overlay" v-if="!article.coverUrl"></div>
            <h2 class="cover-title" v-if="!article.coverUrl">封面</h2>
          </div>

          <!-- 标题区域 -->
          <div class="info-card title-card">
            <label class="info-label">标题</label>
            <div class="title-content">{{ article.title }}</div>
          </div>

          <!-- 摘要区域 -->
          <div class="info-card abstract-card">
            <label class="info-label">摘要</label>
            <div class="abstract-content">
              {{ article.summary }}
            </div>
          </div>

          <!-- 评论输入栏 - 固定在右侧面板底部 -->
          <div
              class="reply-input-container"
              :style="{ width: replyInputWidth-50 + 'px' }"
          >
            <div class="reply-input">
              <div class="reply-input-content">
          <textarea
              ref="commentTextareaRef"
              v-model="commentText"
              class="comment-textarea"
              placeholder="输入你的评论..."
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

        <!-- 评论区 -->
        <!-- 传入文章的ID -->
        <div class="other-card">
          <comment-section :article-key="String(article.id || route.params.id || '')"></comment-section>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted, watch, nextTick} from 'vue';
import {useRoute} from 'vue-router';
import {getArticleDetail} from '../api/article';
import {createComment} from '../api/comment';
import {useUserStore} from '../api/user';
import { ElMessage as Message } from 'element-plus';
import * as marked from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import MarkDownReader from "../components/MarkDownReader.vue";
import CommentSection from "../components/Comment/CommentSection.vue";

// 配置 markdown 渲染
marked.marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, {language: lang}).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
  gfm: true
});

// 获取路由参数
const route = useRoute();
const userStore = useUserStore();

// 文章数据
const article = ref({
  id: null,
  title: '',
  summary: '',
  coverUrl: '',
  content: '',
  status: '',
  publisherId: '' // 与后端字段名一致
});

// 评论输入相关
const commentText = ref('');
const isSubmitting = ref(false);
const commentTextareaRef = ref(null);

// 面板宽度状态
const leftPanelWidth = ref(80);
const rightPanelWidth = ref(20);
const isDragging = ref(false);
const replyInputWidth = ref(0);

// 左侧浏览区缩放相关状态 - 新增
const leftPanelRef = ref(null); // 左侧面板DOM引用
const scaleRatio = ref(1.0); // 缩放比例（默认100%）
const scaleStep = ref(0.1); // 缩放步长（每次10%）
const isCtrlPressed = ref(false); // Ctrl键是否按下

// 获取文章详情
const fetchArticleDetail = async () => {
  const loading = ref(true);
  const errorMsg = ref('');

  try {
    const articleId = route.params.id;
    if (!articleId) throw new Error('文章ID不存在');
    if (isNaN(Number(articleId))) throw new Error(`文章ID格式错误：${articleId}`);

    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('请求超时')), 10000);
    });
    const response = await Promise.race([
      getArticleDetail(articleId),
      timeoutPromise
    ]);

    if (!response || !response.data) throw new Error('接口未返回有效数据');
    const articleData = response.data;
    const requiredFields = ['id', 'title', 'content'];
    const missingFields = requiredFields.filter(field => articleData[field] === undefined);
    if (missingFields.length > 0) throw new Error(`文章数据缺少核心字段：${missingFields.join(', ')}`);

    // 修正：校验后端返回的 publisherId 字段（而非 publisher）
    if (!articleData.publisherId) {
      console.warn(`警告：文章ID ${articleId} 缺少 publisherId 字段（作者ID），无法发表评论`);
      Message.warning('文章作者信息不完整，可能无法发表评论');
    }

    // 修正：赋值 publisherId（与后端字段一致）
    article.value = {
      ...articleData,
      summary: articleData.summary || articleData.abstract || articleData.description || '',
      publisherId: articleData.publisherId || '' // 关键：接收后端的 publisherId 字段
    };
    errorMsg.value = '';

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    errorMsg.value = errorMessage;
    // 修正：错误重置时补充 publisherId 字段
    article.value = {
      id: null,
      title: '',
      summary: '',
      coverUrl: '',
      content: '',
      status: '',
      publisherId: '' // 同步修改
    };
  } finally {
    loading.value = false;
  }

  return {loading, errorMsg};
};
// 分隔线拖动逻辑（原有）
const startDrag = (e) => {
  isDragging.value = true;
  e.preventDefault();
  document.body.style.cursor = 'col-resize';
};

const handleDrag = (e) => {
  if (!isDragging.value) return;

  const container = document.querySelector('.container');
  if (!container) return;

  const containerWidth = container.offsetWidth;
  const newLeftWidth = (e.clientX / containerWidth) * 100;

  if (newLeftWidth >= 20 && newLeftWidth <= 80) {
    leftPanelWidth.value = newLeftWidth;
    rightPanelWidth.value = 100 - newLeftWidth;
    updateReplyInputWidth();
  }
};

const stopDrag = () => {
  isDragging.value = false;
  document.body.style.cursor = '';
};

// 更新评论输入栏宽度（原有）
const updateReplyInputWidth = () => {
  nextTick(() => {
    const rightPanel = document.querySelector('.right-panel');
    if (rightPanel) {
      const panelRect = rightPanel.getBoundingClientRect();
      replyInputWidth.value = panelRect.width;
    }
  });
};

watch(rightPanelWidth, () => {
  updateReplyInputWidth();
}, {immediate: false});

// 左侧浏览区缩放逻辑 - 新增
const handleKeyDown = (e) => {
  // 监听Ctrl键按下
  if (e.ctrlKey || e.metaKey) {
    isCtrlPressed.value = true;
  }
};

const handleKeyUp = (e) => {
  // 监听Ctrl键松开
  if (!e.ctrlKey && !e.metaKey) {
    isCtrlPressed.value = false;
  }
};

const handleLeftPanelWheel = (e) => {
  // 仅当Ctrl键按下且在左侧面板内滚动时生效
  if (isCtrlPressed.value) {
    e.preventDefault();
    e.stopPropagation();

    // 滚轮向上：放大，向下：缩小
    const delta = e.deltaY > 0 ? -scaleStep.value : scaleStep.value;
    // 限制缩放范围：0.5-2.0（50%-200%）
    scaleRatio.value = Math.min(Math.max(scaleRatio.value + delta, 0.5), 2.0);
  }
};

// 自动调整textarea高度（原有）
const autoResizeTextarea = () => {
  nextTick(() => {
    const textarea = commentTextareaRef.value;
    if (textarea) {
      textarea.style.height = 'auto';
      const minHeight = 100;
      const newHeight = Math.max(minHeight, textarea.scrollHeight);
      const maxHeight = 200;
      textarea.style.height = Math.min(newHeight, maxHeight) + 'px';
      textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
    }
  });
};

// 提交评论
const handleSubmitComment = async () => {
  const text = commentText.value.trim();
  if (!text || isSubmitting.value) return;

  // 修正：校验 publisherId（而非 publisher）
  if (!article.value.publisherId) {
    Message.error('文章作者信息缺失，无法发表评论');
    return; // 直接阻断提交，避免向后端传递空的replyUserId
  }

  // 检查用户是否登录（原有逻辑保留）
  if (!userStore.isLogin || !userStore.userId) {
    Message.warning('请先登录后再发表评论');
    return;
  }

  // 检查文章ID是否存在（原有逻辑保留）
  const articleId = article.value.id || route.params.id;
  if (!articleId) {
    Message.error('文章ID不存在，无法发表评论');
    return;
  }

  try {
    isSubmitting.value = true;

    const commentData = {
      content: text,
      articleId: String(articleId),
      userId: userStore.userId,
      parentId: null, // 顶级评论，没有父评论
      replyUserId: article.value.publisherId // 修正：使用 publisherId 作为回复目标ID
    };

    const result = await createComment(commentData);

    // 处理API响应（根据实际后端返回格式调整）
    if (result && (result.code === 200 || result.id)) {
      // Message.success('评论发表成功');
      commentText.value = '';
      if (commentTextareaRef.value) {
        commentTextareaRef.value.style.height = '100px';
        commentTextareaRef.value.style.overflowY = 'hidden';
      }
      
      // 关键修改：将新评论数据通过事件传递
      // 优先使用接口返回的数据，如果接口返回了完整评论数据则使用，否则构造新评论对象
      let newComment;
      if (result.data && result.data.id) {
        // 如果接口返回了完整的评论数据
        newComment = result.data;
        // 确保有 createdAt 字段（兼容 createTime）
        if (!newComment.createdAt && newComment.createTime) {
          newComment.createdAt = newComment.createTime;
        } else if (!newComment.createdAt) {
          newComment.createdAt = new Date().toISOString();
        }
      } else {
        // 否则根据接口返回的ID和当前数据构造新评论对象
        const now = new Date().toISOString();
        newComment = {
          id: result.id || result.data?.id, // 评论ID
          content: text, // 评论内容
          userId: userStore.userId, // 当前用户ID
          articleId: String(articleId),
          parentId: null,
          replyUserId: article.value.publisherId,
          createdAt: result.data?.createdAt || result.data?.createTime || now, // 使用 createdAt 字段（CommentCard 使用此字段）
          // 补充用户名等必要字段
          user: {
            id: userStore.userId,
            name: userStore.username || '匿名用户', // userStore 使用 username 字段
            avatarUrl: userStore.avatarUrl || '/user-avatar.png'
          }
        };
      }
      
      // 触发事件时携带新评论数据
      window.dispatchEvent(new CustomEvent('comment-submitted-root', {
        detail: newComment
      }));
    } else {
      throw new Error(result?.message || '评论发表失败');
    }
  } catch (error) {
    console.error('发表评论失败:', error);
    // 原有错误处理逻辑保留（优化空值判断）
    const errorMsg = error
        ? (error.response?.data?.message || error.message || '发表评论失败，请重试')
        : '发表评论失败，请重试';
    Message.error(errorMsg);
  } finally {
    isSubmitting.value = false;
  }
};
// 挂载时初始化（新增缩放事件监听）
onMounted(() => {
  // 原有事件监听
  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
  fetchArticleDetail();
  window.addEventListener('resize', updateReplyInputWidth);
  setTimeout(() => {
    updateReplyInputWidth();
    if (commentTextareaRef.value) {
      commentTextareaRef.value.style.height = '100px';
    }
  }, 200);

  // 新增缩放相关事件监听
  document.addEventListener('keydown', handleKeyDown);
  document.addEventListener('keyup', handleKeyUp);
  // 仅给左侧面板添加滚轮事件
  if (leftPanelRef.value) {
    leftPanelRef.value.addEventListener('wheel', handleLeftPanelWheel, {passive: false});
  }
});

// 卸载时清理（新增缩放事件移除）
onUnmounted(() => {
  // 原有事件移除
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
  window.removeEventListener('resize', updateReplyInputWidth);

  // 新增缩放相关事件移除
  document.removeEventListener('keydown', handleKeyDown);
  document.removeEventListener('keyup', handleKeyUp);
  if (leftPanelRef.value) {
    leftPanelRef.value.removeEventListener('wheel', handleLeftPanelWheel);
  }
});
</script>

<style>

/* 评论输入栏主体 - 毛玻璃核心样式 */
.reply-input {
  background-color: rgba(255, 255, 255, 0); /* 半透明白色，保证毛玻璃通透感 */
  backdrop-filter: blur(10px); /* 核心模糊效果 */
  -webkit-backdrop-filter: blur(10px); /* Safari 兼容 */
  border: 1px solid rgba(255, 255, 255, 0); /* 半透明白边，增强玻璃质感 */
  flex-direction: column;
  gap: 10px;
  padding: 14px 16px;
  display: flex;
  height: 100%;
  box-sizing: border-box;
}

/* 输入框+按钮容器 - 优化布局 */
.reply-input-content {
  width: 100%;
  flex: 1;
  display: flex;
  align-items: flex-end; /* 按钮与输入框底部对齐 */
  gap: 8px; /* 输入框与按钮间距 */
}

/* 评论输入框 - 自适应高度+质感优化 */
.comment-textarea {
  flex: 1; /* 占满剩余宽度 */
  min-height: 56px; /* 优化基础高度，更舒适 */
  max-height: 150px; /* 合理最大高度，避免过高 */
  padding: 12px 14px;
  border: 1px solid rgba(203, 213, 225, 0.6); /* 半透明边框 */
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #1e293b;
  background-color: rgba(248, 250, 252, 0.7); /* 输入框轻微毛玻璃 */
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  resize: none;
  font-family: inherit;
  box-sizing: border-box;
  transition: all 0.2s ease;
  overflow-y: hidden; /* 隐藏滚动条，自适应高度 */
}

/* 输入框聚焦状态 - 增强反馈 */
.comment-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15); /* 更明显的聚焦阴影 */
  background-color: rgba(255, 255, 255, 0.9); /* 聚焦时背景更实，提升可读性 */
}

.comment-textarea::placeholder {
  color: #94a3b8;
  font-size: 13px;
}

/* 底部信息栏 - 优化布局和提示 */
.reply-input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 11px;
}

.char-count {
  color: #94a3b8;
  font-weight: 500;
}

/* 快捷键提示 - 新增，提升交互体验 */
.shortcut-tip {
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.shortcut-tip::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: #94a3b8;
}

/* 发送按钮 - 优化尺寸和质感 */
.submit-btn {
  padding: 8px 20px; /* 调整padding，适配不同宽度 */
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); /* 更细腻的过渡曲线 */
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  flex-shrink: 0; /* 防止按钮被挤压 */
  white-space: nowrap; /* 避免按钮文字换行 */
}

.submit-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(59, 130, 246, 0.2);
}

.submit-btn:disabled {
  background: #f1f5f9;
  color: #94a3b8;
  cursor: not-allowed;
  opacity: 0.9;
  box-shadow: none;
}

/* 为评论区添加底部padding，避免被输入栏遮挡 */
.other-card {
  padding-bottom: 140px !important; /* 适配容器最小高度+内边距，留出足够空间 */
  box-sizing: border-box;
}

/* 响应式优化 - 分断点细化适配 */
@media (max-width: 1024px) {
  .reply-input-container {
    width: 25% !important; /* 适配右侧面板宽度变化 */
  }
}

@media (max-width: 768px) {
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
    display: none; /* 移动端隐藏快捷键提示，节省空间 */
  }
}

@media (max-width: 480px) {
  .reply-input-content {
    flex-direction: column; /* 移动端输入框和按钮垂直排列 */
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
    padding-bottom: 160px !important; /* 适配移动端垂直布局的高度 */
  }
}

/* 基础样式 */
.article-view {
  width: 100vw;
  height: 93vh;
  overflow: hidden;
  background-color: #f5f7fa;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.container {
  display: flex;
  width: 100%;
  height: 100%;
}

/* 左侧面板样式 */
.left-panel {
  height: 100%;
  overflow: hidden;
  background-color: #ffffff;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.03);
  transition: width 0s ease;
}

.markdown-view {
  height: 100%;
  overflow-y: auto;
  padding: 0;
  -webkit-overflow-scrolling: touch; /* iOS 平滑滚动 */
  /* 确保缩放后内容不会溢出面板 */
  position: relative;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 30px;
  line-height: 1.7;
  color: #333842;
  /* 修复缩放后文字模糊问题 */
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  /* 确保缩放时内容居中对齐 */
  box-sizing: border-box;
}

.main-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: #1a1d23;
  letter-spacing: -0.02em;
}

.intro-text {
  font-size: 1.1rem;
  color: #64748b;
  margin-bottom: 30px;
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
  margin: 30px 0;
}

h2 {
  font-size: 1.6rem;
  margin: 30px 0 15px;
  color: #1e293b;
  position: relative;
  padding-bottom: 8px;
}

h2::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 40px;
  height: 3px;
  background-color: #ffffff;
  border-radius: 2px;
}

h3 {
  font-size: 1.3rem;
  margin: 25px 0 12px;
  color: #1e293b;
}

.feature-card {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  border-left: 4px solid #ffffff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.feature-list {
  padding-left: 24px;
  margin: 15px 0;
}

.feature-list li {
  margin: 8px 0;
  position: relative;
}

.feature-list li::before {
  content: '•';
  color: #ffffff;
  font-weight: bold;
  position: absolute;
  left: -20px;
}

.quote-block {
  border-left: 3px solid #94a3b8;
  padding: 15px 20px;
  margin: 25px 0;
  background-color: #f1f5f9;
  border-radius: 0 4px 4px 0;
  color: #334155;
  font-style: italic;
}

.content-section {
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
  transition: background-color 0.2s ease;
}

.content-section:hover {
  background-color: #f8fafc;
}

/* 分隔线样式 */
.resizer {
  width: 4px;
  background-color: #e2e8f0;
  cursor: col-resize;
  user-select: none;
  transition: all 0.2s ease;
  position: relative;
  z-index: 10;
}

.resizer:hover {
  background-color: #94a3b8;
}

.resizer.resizing {
  background-color: #ffffff;
  width: 6px;
}

.resizer-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #ffffff;
  opacity: 0;
  transition: all 0s ease;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.resizer:hover .resizer-dot {
  opacity: 1;
}

/* 右侧面板样式 */
.right-panel {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #f8fafc;
  transition: width 0s ease;
  border-left: 1px solid #e2e8f0;
  -webkit-overflow-scrolling: touch; /* iOS 平滑滚动 */
}

.info-container {
  min-height: 50%;
  padding: 30px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  gap: 25px;
}

/* 封面样式 */
.cover-card {
  height: auto; /* 取消固定高度，由图片高度决定 */
  min-height: 220px; /* 最小高度保证容器美观 */
}

.cover-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  opacity: 0.9;
}

.cover-title {
  position: relative;
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
  text-align: center;
  line-height: 220px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 信息卡片通用样式 */
.info-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.07);
}

.info-label {
  display: block;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #94a3b8;
  margin-bottom: 10px;
  font-weight: 500;
}

/* 标题卡片 */
.title-card {
  text-align: left;
  padding-bottom: 15px;
}

.title-content {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e293b;
  line-height: 1.4;
}

/* 摘要卡片 */
.abstract-card {
  text-align: left;
  flex: 0 0 auto;
}

.abstract-content {
  color: #475569;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* 其他内容卡片 */
.other-card {
  flex: 0 1 auto;
  min-height: 500px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  background-color: #fefefe;
  text-align: center;
  padding: 30px 20px;
}

.other-text {
  color: #64748b;
  margin-bottom: 15px;
  font-size: 1rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 0.85rem;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #f59e0b;
}

/* 滚动条美化 */
.markdown-view::-webkit-scrollbar,
.right-panel::-webkit-scrollbar {
  width: 6px;
}

.markdown-view::-webkit-scrollbar-track,
.right-panel::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.markdown-view::-webkit-scrollbar-thumb,
.right-panel::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.markdown-view::-webkit-scrollbar-thumb:hover,
.right-panel::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.markdown-view::-webkit-scrollbar-button,
.right-panel::-webkit-scrollbar-button {
  height: 5px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-wrapper {
    max-width: 100%;
    padding: 30px 25px;
  }

  .info-container {
    padding: 25px;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .article-view {
    height: auto;
    min-height: 100vh;
  }

  .container {
    flex-direction: column;
  }

  .left-panel, .right-panel {
    width: 100% !important;
    min-height: auto;
  }

  .left-panel {
    height: auto;
    flex: 1 1 auto;
  }

  .right-panel {
    height: auto;
    order: -1; /* 将右侧面板移到顶部 */
  }

  .resizer {
    display: none; /* 移动端隐藏分隔线 */
  }

  .content-wrapper {
    padding: 20px 15px;
  }

  .main-title {
    font-size: 1.6rem;
    margin-bottom: 12px;
  }

  .intro-text {
    font-size: 1rem;
    margin-bottom: 20px;
  }

  .divider {
    margin: 20px 0;
  }

  h2 {
    font-size: 1.4rem;
    margin: 20px 0 12px;
  }

  h3 {
    font-size: 1.2rem;
    margin: 18px 0 10px;
  }

  .info-container {
    padding: 20px 15px;
    gap: 15px;
  }

  .cover-card {
    min-height: 180px;
  }

  .info-card {
    padding: 15px;
  }

  .info-label {
    font-size: 0.8rem;
    margin-bottom: 8px;
  }

  .title-content {
    font-size: 1.1rem;
  }

  .abstract-content {
    font-size: 0.9rem;
  }

  .other-card {
    padding: 20px 15px;
  }

  .other-text {
    font-size: 0.9rem;
    margin-bottom: 12px;
  }

  .cover-title {
    font-size: 1.2rem;
    line-height: 180px;
  }
}

@media (max-width: 480px) {
  .article-view {
    height: auto;
  }

  .content-wrapper {
    padding: 15px 10px;
  }

  .main-title {
    font-size: 1.4rem;
    margin-bottom: 10px;
  }

  .intro-text {
    font-size: 0.9rem;
    margin-bottom: 15px;
  }

  .divider {
    margin: 15px 0;
  }

  h2 {
    font-size: 1.2rem;
    margin: 15px 0 10px;
  }

  h3 {
    font-size: 1.1rem;
    margin: 15px 0 8px;
  }

  .feature-card {
    padding: 15px;
    margin: 15px 0;
  }

  .quote-block {
    padding: 12px 15px;
    margin: 20px 0;
  }

  .info-container {
    padding: 15px 10px;
    gap: 12px;
  }

  .cover-card {
    min-height: 150px;
  }

  .info-card {
    padding: 12px;
  }

  .info-label {
    font-size: 0.75rem;
    margin-bottom: 6px;
  }

  .title-content {
    font-size: 1rem;
  }

  .abstract-content {
    font-size: 0.85rem;
  }

  .other-card {
    padding: 8px 5px;
    width: 100%;
    height: 1000px;
  }

  .other-text {
    font-size: 0.85rem;
    margin-bottom: 10px;
  }

  .status-indicator {
    font-size: 0.8rem;
    gap: 6px;
  }

  .cover-title {
    font-size: 1rem;
    line-height: 150px;
  }

  .cover-image {
    max-height: 200px;
  }
}

.article-content {
  line-height: 1.8;
  color: #333842;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.article-content h2,
.article-content h3,
.article-content p,
.article-content ul,
.article-content ol {
  margin-bottom: 16px;
}

.article-content img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
  display: block;
}

.article-content pre {
  background-color: #f8fafc;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  margin: 16px 0;
  -webkit-overflow-scrolling: touch;
  max-width: 100%;
}

.article-content code {
  font-family: 'Fira Code', monospace;
  font-size: 0.9em;
}

@media (max-width: 768px) {
  .article-content {
    line-height: 1.6;
  }

  .article-content pre {
    padding: 12px;
    margin: 12px 0;
  }

  .article-content code {
    font-size: 0.85em;
  }
}

@media (max-width: 480px) {
  .article-content img {
    margin: 12px 0;
  }

  .article-content pre {
    padding: 10px;
    margin: 10px 0;
  }

  .article-content code {
    font-size: 0.8em;
  }
}

.cover-image {
  width: 100%;
  height: auto;
  max-height: 280px;
  object-fit: contain;
  object-position: center;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .cover-image {
    max-height: 240px;
  }
}

@media (max-width: 480px) {
  .cover-image {
    max-height: 180px;
  }
}

.status-dot.published {
  background-color: #52c41a;
}

.status-dot.draft {
  background-color: #faad14;
}

.status-dot.disabled {
  background-color: #f5222d;
}

</style>