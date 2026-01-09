<template>
  <div class="article-view">
    <div class="container">
      <!-- 左侧浏览区 -->
      <div
          class="left-panel"
          :style="{ width: leftPanelWidth + '%' }"
          ref="leftPanelRef"
      >
        <div class="markdown-view">
          <!-- 缩放容器 -->
          <div
              class="content-wrapper"
              :style="{
                transform: `scale(${scaleRatio})`,
                transformOrigin: 'top center',
                transition: 'transform 0.2s ease',
                display: 'inline-block',
                width: '100%',
                boxSizing: 'border-box'
              }"
          >
            <!-- 移动端专属：封面展示 -->
            <div v-if="isMobile" class="mobile-cover-section">
              <div class="cover-card">
                <img
                    :src="article.coverUrl ? `${apiBaseUrl}${article.coverUrl}` : ''"
                    class="cover-image"
                    v-if="article.coverUrl"
                    :alt="article.title"
                />
                <div class="cover-overlay" v-if="!article.coverUrl"></div>
                <h2 class="cover-title" v-if="!article.coverUrl">封面</h2>
              </div>
            </div>

            <!-- 移动端专属：摘要展示 -->
            <div v-if="isMobile" class="mobile-abstract-section">
              <div class="info-card abstract-card">
                <label class="info-label">摘要</label>
                <div class="abstract-content">
                  {{ article.summary }}
                </div>
              </div>
            </div>

            <!-- 通用内容区域 -->
            <h1 class="main-title">{{ article.title }}</h1>
            <p class="intro-text" v-if="!isMobile">
              {{ article.summary }}
            </p>

            <div class="divider"></div>
            <mark-down-reader :content="article.content"></mark-down-reader>

            <!-- 移动端专属：评论输入和评论区 -->
            <div v-if="isMobile" class="mobile-comment-section">
              <!-- 评论输入栏 -->
              <div class="reply-input-container" :style="{ width: '100%' }">
                <div class="reply-input">
                  <div class="reply-input-content">
                    <textarea
                        ref="mobileCommentTextareaRef"
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

              <!-- 评论区 -->
              <div class="other-card">
                <comment-section :article-key="String(article.id || route.params.id || '')"></comment-section>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分隔线 -->
      <div
          class="resizer"
          @mousedown="startDrag"
          :class="{ 'resizing': isDragging }"
          v-if="!isMobile"
      >
        <div class="resizer-dot"></div>
      </div>

      <!-- 右侧信息区（桌面端专属） -->
      <div
          class="right-panel"
          :style="{
            width: rightPanelWidth + '%',
            '--right-panel-width-value': rightPanelWidth + '%'
          }"
          v-if="!isMobile"
      >
        <div class="info-container">
          <!-- 封面区域 -->
          <div class="cover-card">
            <img
                :src="article.coverUrl ? `${apiBaseUrl}${article.coverUrl}` : ''"
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

          <!-- 评论输入栏 -->
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
        <div class="other-card">
          <comment-section :article-key="String(article.id || route.params.id || '')"></comment-section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted, nextTick, watch} from 'vue';
import {useRoute} from 'vue-router';
import {getArticleDetail} from '../api/article';
import {createComment} from '../api/comment';
import {useUserStore} from '../api/user';
import { ElMessage as Message } from 'element-plus';
import * as marked from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';
import MarkDownReader from "@/components/Article/MarkDownReader.vue";
import CommentSection from "../components/Comment/CommentSection.vue";
import { getApiBaseUrl } from '../utils/apiConfig';

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

// API 基础地址
const apiBaseUrl = getApiBaseUrl();

// 文章数据
const article = ref({
  id: null,
  title: '',
  summary: '',
  coverUrl: '',
  content: '',
  status: '',
  publisherId: ''
});

// 移动端检测
const isMobile = ref(false);
const checkIsMobile = () => {
  isMobile.value = window.innerWidth <= 768;
};

// 评论输入相关
const commentText = ref('');
const isSubmitting = ref(false);
const commentTextareaRef = ref(null);
const mobileCommentTextareaRef = ref(null);

// 面板宽度状态
const leftPanelWidth = ref(80);
const rightPanelWidth = ref(20);
const isDragging = ref(false);
const replyInputWidth = ref(0);

// 左侧浏览区缩放相关状态
const leftPanelRef = ref(null);
const scaleRatio = ref(1.0);
const scaleStep = ref(0.1);
const isCtrlPressed = ref(false);

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

    if (!articleData.publisherId) {
      console.warn(`警告：文章ID ${articleId} 缺少 publisherId 字段（作者ID），无法发表评论`);
      Message.warning('文章作者信息不完整，可能无法发表评论');
    }

    article.value = {
      ...articleData,
      summary: articleData.summary || articleData.abstract || articleData.description || '',
      publisherId: articleData.publisherId || ''
    };
    errorMsg.value = '';

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : '未知错误';
    errorMsg.value = errorMessage;
    article.value = {
      id: null,
      title: '',
      summary: '',
      coverUrl: '',
      content: '',
      status: '',
      publisherId: ''
    };
  } finally {
    loading.value = false;
  }

  return {loading, errorMsg};
};

// 分隔线拖动逻辑
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

// 更新评论输入栏宽度
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

// 左侧浏览区缩放逻辑
const handleKeyDown = (e) => {
  if (e.ctrlKey || e.metaKey) {
    isCtrlPressed.value = true;
  }
};

const handleKeyUp = (e) => {
  if (!e.ctrlKey && !e.metaKey) {
    isCtrlPressed.value = false;
  }
};

const handleLeftPanelWheel = (e) => {
  if (isCtrlPressed.value) {
    e.preventDefault();
    e.stopPropagation();

    const delta = e.deltaY > 0 ? -scaleStep.value : scaleStep.value;
    scaleRatio.value = Math.min(Math.max(scaleRatio.value + delta, 0.5), 2.0);
  }
};

// 自动调整textarea高度
const autoResizeTextarea = () => {
  nextTick(() => {
    const textareas = [commentTextareaRef.value, mobileCommentTextareaRef.value].filter(Boolean);
    textareas.forEach(textarea => {
      if (textarea) {
        textarea.style.height = 'auto';
        const minHeight = 100;
        const newHeight = Math.max(minHeight, textarea.scrollHeight);
        const maxHeight = 200;
        textarea.style.height = Math.min(newHeight, maxHeight) + 'px';
        textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden';
      }
    });
  });
};

// 提交评论
const handleSubmitComment = async () => {
  const text = commentText.value.trim();
  if (!text || isSubmitting.value) return;

  if (!article.value.publisherId) {
    Message.error('文章作者信息缺失，无法发表评论');
    return;
  }

  if (!userStore.isLogin || !userStore.userId) {
    Message.warning('请先登录后再发表评论');
    return;
  }

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
      parentId: null,
      replyUserId: article.value.publisherId
    };

    const result = await createComment(commentData);

    if (result && (result.code === 200 || result.id)) {
      commentText.value = '';
      const textareas = [commentTextareaRef.value, mobileCommentTextareaRef.value].filter(Boolean);
      textareas.forEach(textarea => {
        if (textarea) {
          textarea.style.height = '100px';
          textarea.style.overflowY = 'hidden';
        }
      });

      let newComment;
      if (result.data && result.data.id) {
        newComment = result.data;
        if (!newComment.createdAt && newComment.createTime) {
          newComment.createdAt = newComment.createTime;
        } else if (!newComment.createdAt) {
          newComment.createdAt = new Date().toISOString();
        }
      } else {
        const now = new Date().toISOString();
        newComment = {
          id: result.id || result.data?.id,
          content: text,
          userId: userStore.userId,
          articleId: String(articleId),
          parentId: null,
          replyUserId: article.value.publisherId,
          createdAt: result.data?.createdAt || result.data?.createTime || now,
          user: {
            id: userStore.userId,
            name: userStore.username || '匿名用户',
            avatarUrl: userStore.avatarUrl || '/user-avatar.png'
          }
        };
      }

      window.dispatchEvent(new CustomEvent('comment-submitted-root', {
        detail: newComment
      }));
    } else {
      throw new Error(result?.message || '评论发表失败');
    }
  } catch (error) {
    console.error('发表评论失败:', error);
    const errorMsg = error
        ? (error.response?.data?.message || error.message || '发表评论失败，请重试')
        : '发表评论失败，请重试';
    Message.error(errorMsg);
  } finally {
    isSubmitting.value = false;
  }
};

// 窗口大小变化处理
const handleResize = () => {
  checkIsMobile();
  updateReplyInputWidth();
};

// 挂载时初始化
onMounted(() => {
  checkIsMobile();

  document.addEventListener('mousemove', handleDrag);
  document.addEventListener('mouseup', stopDrag);
  window.addEventListener('resize', handleResize);
  document.addEventListener('keydown', handleKeyDown);
  document.addEventListener('keyup', handleKeyUp);

  if (leftPanelRef.value) {
    leftPanelRef.value.addEventListener('wheel', handleLeftPanelWheel, {passive: false});
  }

  fetchArticleDetail();

  setTimeout(() => {
    updateReplyInputWidth();
    const textareas = [commentTextareaRef.value, mobileCommentTextareaRef.value].filter(Boolean);
    textareas.forEach(textarea => {
      if (textarea) {
        textarea.style.height = '100px';
      }
    });
  }, 200);

  window.dispatchEvent(new CustomEvent('toggle-navbar', {
    detail: {collapsed: true}
  }));
});

// 卸载时清理
onUnmounted(() => {
  document.removeEventListener('mousemove', handleDrag);
  document.removeEventListener('mouseup', stopDrag);
  window.removeEventListener('resize', handleResize);
  document.removeEventListener('keydown', handleKeyDown);
  document.removeEventListener('keyup', handleKeyUp);

  if (leftPanelRef.value) {
    leftPanelRef.value.removeEventListener('wheel', handleLeftPanelWheel);
  }

  window.dispatchEvent(new CustomEvent('toggle-navbar', {
    detail: {collapsed: false}
  }));
});
</script>

<style>
/* 移动端顶部区域样式 */
.mobile-cover-section {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.mobile-abstract-section {
  margin-bottom: 30px;
}

.mobile-comment-section {
  margin-top: 40px;
  border-top: 1px solid #555;
  padding-top: 30px;
}

/* 移动端封面卡片调整 */
.mobile-cover-section .cover-card {
  height: auto;
  min-height: 200px;
  background-color: #2d2d2d;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.mobile-cover-section .cover-image {
  max-height: 250px;
  width: 100%;
  object-fit: contain;
  border-radius: 8px;
}

/* 移动端摘要卡片调整 */
.mobile-abstract-section .abstract-card {
  background-color: #2d2d2d;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* 移动端评论区域调整 */
.mobile-comment-section .reply-input-container {
  width: 100% !important;
  margin-bottom: 30px;
}

.mobile-comment-section .other-card {
  padding-bottom: 20px !important;
}

/* 基础样式 */
.article-view {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #1a1a1a;
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
  background-color: #1e1e1e;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
  transition: width 0s ease;
}

.markdown-view {
  height: 100%;
  overflow-y: auto;
  padding: 0;
  -webkit-overflow-scrolling: touch;
  position: relative;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 30px;
  line-height: 1.7;
  color: #e0e0e0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  box-sizing: border-box;
}

.main-title {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 16px;
  color: #e0e0e0;
  letter-spacing: -0.02em;
}

.intro-text {
  font-size: 1.1rem;
  color: #999;
  margin-bottom: 30px;
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #555, transparent);
  margin: 30px 0;
}

h2 {
  font-size: 1.6rem;
  margin: 30px 0 15px;
  color: #e0e0e0;
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
  background-color: #4fc3f7;
  border-radius: 2px;
}

h3 {
  font-size: 1.3rem;
  margin: 25px 0 12px;
  color: #e0e0e0;
}

.feature-card {
  background-color: #2d2d2d;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  border-left: 4px solid #4fc3f7;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
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
  color: #4fc3f7;
  font-weight: bold;
  position: absolute;
  left: -20px;
}

.quote-block {
  border-left: 3px solid #4fc3f7;
  padding: 15px 20px;
  margin: 25px 0;
  background-color: #2d2d2d;
  border-radius: 0 4px 4px 0;
  color: #ccc;
  font-style: italic;
}

.content-section {
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
  transition: background-color 0.2s ease;
}

.content-section:hover {
  background-color: #2d2d2d;
}

/* 分隔线样式 */
.resizer {
  width: 4px;
  background-color: #555;
  cursor: col-resize;
  user-select: none;
  transition: all 0.2s ease;
  position: relative;
  z-index: 10;
}

.resizer:hover {
  background-color: #777;
}

.resizer.resizing {
  background-color: #4fc3f7;
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
  background-color: #4fc3f7;
  opacity: 0;
  transition: all 0s ease;
  box-shadow: 0 0 0 3px rgba(79, 195, 247, 0.3);
}

.resizer:hover .resizer-dot {
  opacity: 1;
}

/* 右侧面板样式 */
.right-panel {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  background-color: #1a1a1a;
  transition: width 0s ease;
  border-left: 1px solid #555;
  -webkit-overflow-scrolling: touch;
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
  height: auto;
  min-height: 220px;
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
  background-color: #2d2d2d;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}

.info-label {
  display: block;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #999;
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
  color: #e0e0e0;
  line-height: 1.4;
}

/* 摘要卡片 */
.abstract-card {
  text-align: left;
  flex: 0 0 auto;
}

.abstract-content {
  color: #ccc;
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
  background-color: #1e1e1e;
  text-align: center;
  padding: 30px 20px;
}

.other-text {
  color: #999;
  margin-bottom: 15px;
  font-size: 1rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #999;
  font-size: 0.85rem;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #f59e0b;
}

/* 评论输入栏主体 */
.reply-input {
  background-color: rgba(30, 30, 30, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(100, 100, 100, 0.3);
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

.comment-textarea {
  flex: 1;
  min-height: 56px;
  max-height: 150px;
  padding: 12px 14px;
  border: 1px solid rgba(100, 100, 100, 0.5);
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #e0e0e0;
  background-color: rgba(45, 45, 45, 0.8);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  resize: none;
  font-family: inherit;
  box-sizing: border-box;
  transition: all 0.2s ease;
  overflow-y: hidden;
}

.comment-textarea:focus {
  outline: none;
  border-color: #4fc3f7;
  box-shadow: 0 0 0 3px rgba(79, 195, 247, 0.2);
  background-color: rgba(45, 45, 45, 0.95);
}

.comment-textarea::placeholder {
  color: #888;
  font-size: 13px;
}

.reply-input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 11px;
}

.char-count {
  color: #999;
  font-weight: 500;
}

.shortcut-tip {
  color: #888;
  display: flex;
  align-items: center;
  gap: 4px;
}

.shortcut-tip::before {
  content: '';
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: #999;
}

.submit-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
  flex-shrink: 0;
  white-space: nowrap;
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
  background: #2d2d2d;
  color: #666;
  cursor: not-allowed;
  opacity: 0.9;
  box-shadow: none;
}

.other-card {
  padding-bottom: 140px !important;
  box-sizing: border-box;
}

/* 滚动条美化 */
.markdown-view::-webkit-scrollbar,
.right-panel::-webkit-scrollbar {
  width: 6px;
}

.markdown-view::-webkit-scrollbar-track,
.right-panel::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.markdown-view::-webkit-scrollbar-thumb,
.right-panel::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 3px;
}

.markdown-view::-webkit-scrollbar-thumb:hover,
.right-panel::-webkit-scrollbar-thumb:hover {
  background: #777;
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

/* 移动端响应式设计 */
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
    display: none;
  }

  .resizer {
    display: none;
  }

  .content-wrapper {
    padding: 20px 15px;
    max-width: 100%;
  }

  .main-title {
    font-size: 1.6rem;
    margin-bottom: 12px;
  }

  .intro-text {
    font-size: 1rem;
    margin-bottom: 20px;
    display: none;
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

  .mobile-cover-section {
    margin-bottom: 15px;
  }

  .mobile-abstract-section {
    margin-bottom: 20px;
  }

  .mobile-comment-section {
    margin-top: 30px;
    padding-top: 20px;
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

  .mobile-cover-section .cover-card {
    min-height: 150px;
  }

  .mobile-abstract-section .abstract-card {
    padding: 15px;
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
    height: auto;
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
  color: #e0e0e0;
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
  background-color: #2d2d2d;
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