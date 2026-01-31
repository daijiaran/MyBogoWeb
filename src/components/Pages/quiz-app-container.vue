<template>
  <div class="quiz-app-container">
    <div
        v-if="isMobile && (!leftSidebarCollapsed || !rightSidebarCollapsed)"
        class="mobile-backdrop"
        @click="closeAllSidebars"
    ></div>

    <header>
      <button class="icon-btn mobile-menu-btn" @click="toggleLeftSidebar">
        ☰
      </button>

      <div class="app-brand">
        <h1>📋 <span class="brand-text">刷题工具</span></h1>
      </div>

      <div v-if="currentQuizId" class="quiz-header-wrapper">
        <div class="quiz-info-group">
          <span v-if="!isMobile" class="quiz-title" :title="currentQuiz.title">{{ currentQuiz.title }}</span>
          <span v-if="isViewingWrongOnly" class="tag mode-badge">错题</span>
        </div>

        <div class="quiz-action-group">
          <div v-if="!isMobile && currentQuiz.isSubmitted && !isViewingWrongOnly" class="score-board">
            <span class="score-highlight">{{ currentScore }}</span>/{{ currentTotal }}
          </div>

          <template v-if="!isMobile">
            <div v-if="currentQuiz.isSubmitted" class="divider"></div>
            <div class="divider"></div>
            <button class="btn secondary sm" @click="toggleQuizMode" :class="{ 'active': quizMode === 'single' }">
              {{ quizMode === 'scroll' ? '单题' : '滚动' }}模式
            </button>
            <div class="divider"></div>
            <button v-if="!currentQuiz.isSubmitted" class="btn sm" @click="submitQuiz">提交</button>
            <template v-else>
              <button v-if="!isViewingWrongOnly" class="btn secondary sm" @click="resetCurrentQuiz">重做</button>
              <button v-if="isViewingWrongOnly" class="btn secondary sm" @click="resetWrongQuestions">重刷错题</button>
            </template>
          </template>
        </div>
            
            <!-- 下一题按钮 -->
<!--            <div v-if="showNextButton && !currentQuiz.isSubmitted" class="next-question-btn-container">-->
<!--              <button class="btn primary full-width shadow-btn next-btn" @click="goToNextQuestion">-->
<!--                {{ currentQuestionIndex < questionsToShow.length - 1 ? '下一题' : '完成答题' }}-->
<!--              </button>-->
<!--            </div>-->
          </div>

      <div class="header-right-actions">
        <button 
          class="icon-btn" 
          @click="$router.push('/sql')" 
          title="SQL 语法练习"
          style="font-size: 1.2rem; margin-right: 4px;"
        >
          💾SQL 语法练习
        </button>
        <div v-if="!isMobile" class="auto-scroll-toggle" title="自动滚题">
          <span class="toggle-label">自动滚题</span>
          <label class="toggle-switch">
            <input type="checkbox" v-model="isAutoScroll" @change="toggleAutoScroll">
            <span class="toggle-slider"></span>
          </label>
        </div>
        <button class="icon-btn mobile-err-btn" @click="toggleRightSidebar">
          ❌
        </button>
        <button class="theme-toggle" @click="toggleTheme" title="切换深色/浅色模式">
          {{ isDark ? '☀️' : '🌙' }}
        </button>
      </div>
    </header>

    <!-- 多选题提示 -->
    <div v-if="showMultiChoiceHint" class="multi-choice-hint">
      <div class="hint-content">
        <span class="hint-icon">ℹ️</span>
        <span class="hint-text">当前为多选题，已暂停自动跳转</span>
      </div>
    </div>

    <div class="app-layout">
      <aside class="sidebar left-sidebar" :class="{ collapsed: leftSidebarCollapsed, 'mobile-open': !leftSidebarCollapsed && isMobile }">
        <div class="sidebar-header">
          <span>📚 历史试卷</span>
          <div class="sidebar-header-buttons">
            <button
                class="btn secondary sm new-quiz-btn"
                @click="createNewQuiz"
            >
              新试卷
            </button>
            <button
                class="btn secondary sm new-group-btn"
                @click="createNewGroup"
            >
              新建分组
            </button>
          </div>
        </div>
        <div class="sidebar-content">
          <ul class="sidebar-list">
            <!-- 显示分组列表 -->
            <li
                v-for="group in quizGroups"
                :key="group.id"
                class="sidebar-group"
                draggable="false"
                @dragover="handleDragOver"
                @dragenter="handleDragEnter($event)"
                @dragleave="handleDragLeave($event)"
                @drop="handleDrop($event, group.id)"
            >
              <div class="group-header" :class="{ expanded: group.isExpanded }" @click="toggleGroupExpanded(group.id)">
                <span class="group-icon">{{ group.isExpanded ? '▼' : '▶' }}</span>
                <span class="group-name">{{ group.name }}</span>
                <span class="group-count">({{ group.quizIds.length }})</span>
                <div class="group-actions">
                  <button class="action-btn" @click.stop="renameGroup(group.id)">✏️</button>
                  <button class="action-btn delete" @click.stop="deleteGroup(group.id)">🗑️</button>
                </div>
              </div>
              
              <!-- 分组内的试卷列表 -->
              <ul v-if="group.isExpanded" class="group-quizzes">
                <li
                    v-for="quizId in group.quizIds"
                    :key="quizId"
                    class="sidebar-item group-quiz-item"
                    :class="{ 
                      active: currentQuizId === quizId && !isViewingWrongOnly,
                      'has-progress': quizMode === 'single' && !currentQuiz.isSubmitted && currentQuizId === quizId
                    }"
                    @click="loadQuiz(quizId, false)"
                    @mouseenter="hoveredQuizId = quizId"
                    @mouseleave="hoveredQuizId = null"
                    draggable="true"
                    @dragstart="handleDragStart($event, { id: quizId }, 'quiz')"
                    @dragend="handleDragEnd"
                >
                  <transition name="progress-fade">
                    <span v-show="quizMode === 'single' && !currentQuiz.isSubmitted && currentQuizId === quizId" class="question-progress">
                      {{ currentQuestionIndex + 1 }}/{{ questionsToShow.length }}
                    </span>
                  </transition>
                  <span v-if="getQuizById(quizId)?.isSubmitted" class="score-tag" :class="getScoreClass(getQuizById(quizId))">
                    {{ getQuizScore(getQuizById(quizId)) }}/{{ getQuizById(quizId).questions.length }}
                  </span>
                  <div class="quiz-item-title">{{ getQuizById(quizId)?.title }}</div>
                  <span class="date">
                    {{ formatDate(getQuizById(quizId)?.timestamp) }}
                  </span>
                  <transition name="actions-slide">
                    <div v-show="hoveredQuizId === quizId" class="sidebar-actions">
                      <div class="action-buttons">
                        <button class="action-btn" @click.stop="renameQuiz(quizId)">✏️</button>
                        <button class="action-btn" @click.stop="removeQuizFromGroup(quizId, group.id)">📤</button>
                        <button class="action-btn delete" @click.stop="deleteQuiz(quizId)">🗑️</button>
                      </div>
                    </div>
                  </transition>
                </li>
              </ul>
            </li>
            
            <!-- 未分组的试卷列表 - 直接显示在主列表中 -->
            <li
                v-for="quiz in ungroupedQuizzes"
                :key="quiz.id"
                class="sidebar-item"
                :class="{ 
                  active: currentQuizId === quiz.id && !isViewingWrongOnly,
                  'has-progress': quizMode === 'single' && !currentQuiz.isSubmitted && currentQuizId === quiz.id
                }"
                @click="loadQuiz(quiz.id, false)"
                @mouseenter="hoveredQuizId = quiz.id"
                @mouseleave="hoveredQuizId = null"
                draggable="true"
                @dragstart="handleDragStart($event, quiz, 'quiz')"
                @dragend="handleDragEnd"
            >
              <transition name="progress-fade">
                <span v-show="quizMode === 'single' && !currentQuiz.isSubmitted && currentQuizId === quiz.id" class="question-progress">
                  {{ currentQuestionIndex + 1 }}/{{ questionsToShow.length }}
                </span>
              </transition>
              <span v-if="quiz.isSubmitted" class="score-tag" :class="getScoreClass(quiz)">
                {{ getQuizScore(quiz) }}/{{ quiz.questions.length }}
              </span>
              <div class="quiz-item-title">{{ quiz.title }}</div>
              <span class="date">
                {{ formatDate(quiz.timestamp) }}
              </span>
              <transition name="actions-slide">
                <div v-show="hoveredQuizId === quiz.id" class="sidebar-actions">
                  <div class="action-buttons">
                    <button class="action-btn" @click.stop="renameQuiz(quiz.id)">✏️</button>
                    <button class="action-btn delete" @click.stop="deleteQuiz(quiz.id)">🗑️</button>
                  </div>
                </div>
              </transition>
            </li>
            <li v-if="ungroupedQuizzes.length === 0" class="empty-list-item">暂无未分组试卷</li>
          </ul>
        </div>
        <div class="sidebar-footer">
          <button class="btn secondary sm export-btn "  @click="showExportModal">
            📤 导出/分享
          </button>
        </div>
        <div v-if="!isMobile" class="sidebar-toggle-btn left-toggle" @click="leftSidebarCollapsed = !leftSidebarCollapsed">
          {{ leftSidebarCollapsed ? '▶' : '◀' }}
        </div>
      </aside>

      <main class="main-content">
        <div class="container">

          <div v-if="isCreating || (!currentQuizId && quizHistory.length === 0)" class="importer-section">
            <div class="import-header">
              <h2>新建试卷</h2>
              <label class="btn secondary sm upload-btn">
                📂 上传本地文件 (.txt/.html/.json)
                <input type="file" accept=".txt,.html,.htm,.json" @change="handleFileUpload" style="display: none">
              </label>
            </div>

            <p class="importer-desc">粘贴 HTML 源码，或点击上方按钮上传文件：</p>

            <textarea
                v-model="htmlInput"
                placeholder='<div class="studentTestDetail-content">... 或 <app-object-quiz-item>...'
            ></textarea>

            <div class="btn-group">
              <button class="btn" @click="parseAndGenerate">开始解析</button>
              <button class="btn secondary" @click="showDemoHelp">演示数据</button>
            </div>
            <div v-if="parseError" class="parse-error">{{ parseError }}</div>
          </div>

          <div v-else-if="!currentQuizId && quizHistory.length > 0 && !isCreating">
            <div class="empty-guide">
              <h3 class="default-title">👈 请选择试卷</h3>
              <p v-if="isMobile" style="color: var(--text-secondary)">点击左上角菜单查看历史</p>
            </div>
          </div>

          <div v-if="currentQuizId && currentQuiz" class="quiz-area" :class="{'pb-80': isMobile || showNextButton}">
            <div v-if="questionsToShow.length === 0 && isViewingWrongOnly" class="empty-state">
              🎉 太棒了！本卷没有错题。
            </div>
            <div
                v-for="(q, index) in displayedQuestions"
                :key="q.id"
                class="question-card"
                :class="{
                  'status-correct': currentQuiz.isSubmitted && checkAnswer(q),
                  'status-wrong': currentQuiz.isSubmitted && !checkAnswer(q),
                  'single-mode': quizMode === 'single'
                }"
                @click="closeAllSidebars"
            >
              <div class="q-header">
                <span class="q-index">{{ q.meta || `题目 ${index + 1}` }}</span>
                <span class="tag type">{{ getTypeLabel(q.type) }}</span>
                <button v-if="isViewingWrongOnly && currentQuiz.isSubmitted" class="btn secondary sm remove-btn" @click.stop="removeFromWrongQuestions(q.id)">移除错题本</button>
              </div>
              <div class="q-content" v-html="q.content"></div>

              <div v-if="q.type === 'single'" class="options-list">
                <label v-for="opt in q.options" :key="opt.label" class="option-label" :class="{
                  'correct-option': currentQuiz.isSubmitted && opt.label === q.correctAnswer
                }">
                  <input
                      type="radio"
                      :name="`q-${q.id}`"
                      :value="opt.label"
                      v-model="q.userAnswer"
                      :disabled="currentQuiz.isSubmitted"
                      @change="handleOptionSelect(q, index)"
                  >
                  <span class="option-text"><b>{{ opt.label }}.</b> <span v-html="opt.html"></span></span>
                </label>
              </div>

              <div v-else-if="q.type === 'multiple'" class="options-list">
                <label v-for="opt in q.options" :key="opt.label" class="option-label" :class="{
                  'correct-option': currentQuiz.isSubmitted && (q.correctAnswer || '').split(',').includes(opt.label)
                }">
                  <input
                      type="checkbox"
                      :value="opt.label"
                      :checked="isCheckboxChecked(q, opt.label)"
                      :disabled="currentQuiz.isSubmitted"
                      @change="(e) => { toggleCheckbox(q, opt.label, e.target.checked); handleOptionSelect(q, index); }"
                  >
                  <span class="option-text"><b>{{ opt.label }}.</b> <span v-html="opt.html"></span></span>
                </label>
              </div>

              <div v-else>
                <input
                    type="text"
                    class="short-answer-input"
                    placeholder="请输入答案"
                    v-model="q.userAnswer"
                    :disabled="currentQuiz.isSubmitted"
                    @input="saveHistory"
                    @focus="closeAllSidebars"
                >
              </div>

              <div v-if="currentQuiz.isSubmitted" class="result-analysis">
                <p>
                  <span class="tag correct-ans">正确答案</span>
                  <strong class="break-word">{{ q.correctAnswer }}</strong>
                </p>
                <p>
                  <span class="tag" :class="checkAnswer(q) ? 'correct-ans' : 'wrong-ans'">你的答案</span>
                  <span class="break-word">{{ q.userAnswer || '(未作答)' }}</span>
                </p>
                <div v-if="q.explanation" class="explanation-box">
                  <strong>💡 试题解析</strong>
                  {{ q.explanation }}
                </div>
            </div>
            
            <!-- 下一题按钮 -->
<!--            <div v-if="showNextButton && !currentQuiz.isSubmitted" class="next-question-btn-container">-->
<!--              <button class="btn primary full-width shadow-btn next-btn" @click="goToNextQuestion">-->
<!--                {{ currentQuestionIndex < questionsToShow.length - 1 ? '下一题' : '完成答题' }}-->
<!--              </button>-->
<!--            </div>-->
            
            <!-- 单题模式下的上一题和下一题按钮 -->
            <div v-if="quizMode === 'single' && !currentQuiz.isSubmitted" class="single-mode-nav-btns">
              <button 
                class="btn secondary shadow-btn prev-btn" 
                @click="goToPreviousQuestion"
                :disabled="currentQuestionIndex === 0"
              >
                上一题
              </button>
              <button class="btn primary shadow-btn next-btn" @click="goToNextQuestion">
                {{ currentQuestionIndex < questionsToShow.length - 1 ? '下一题' : '完成答题' }}
              </button>
            </div>
          </div>
        </div>
        </div>
      </main>

      <aside class="sidebar right-sidebar" :class="{ collapsed: rightSidebarCollapsed, 'mobile-open': !rightSidebarCollapsed && isMobile }">
        <div class="sidebar-header">
          <span>❌ 错题本</span>
          <small>只看错题</small>
        </div>
        <div class="sidebar-content">
          <ul class="sidebar-list">
            <li v-if="wrongHistoryItems.length === 0" class="empty-list-item">暂无错题记录 🎉</li>
            <li
                v-for="item in wrongHistoryItems"
                :key="item.id"
                class="sidebar-item"
                :class="{ active: currentQuizId === item.id && isViewingWrongOnly }"
                @click="loadQuiz(item.id, true)"
            >
              <div class="quiz-item-title">{{ item.title }}</div>
              <span class="date">错题数: <span class="wrong-count">{{ item.wrongCount }}</span></span>
            </li>
          </ul>
        </div>
        <div v-if="!isMobile" class="sidebar-toggle-btn right-toggle" @click="rightSidebarCollapsed = !rightSidebarCollapsed">
          {{ rightSidebarCollapsed ? '◀' : '▶' }}
        </div>
      </aside>
    </div>

    <!-- 移动端底部栏 -->
    <div v-if="isMobile" class="mobile-bottom-bar">
      <div class="bottom-bar-left">
        <div class="auto-scroll-toggle" title="自动滚题">
          <span class="toggle-label">自动滚题</span>
          <label class="toggle-switch">
            <input type="checkbox" v-model="isAutoScroll" @change="toggleAutoScroll">
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>
      <div v-if="currentQuizId && currentQuiz.isSubmitted && !isViewingWrongOnly" class="bottom-bar-center">
        <div class="score-board">
          <span class="score-highlight">{{ currentScore }}</span>/{{ currentTotal }}
        </div>
      </div>
      <div class="bottom-bar-right">
        <button v-if="currentQuizId && !currentQuiz.isSubmitted" class="btn sm" @click="submitQuiz">提交判卷</button>
        <template v-else-if="currentQuizId && currentQuiz.isSubmitted">
          <button v-if="!isViewingWrongOnly" class="btn secondary sm" @click="resetCurrentQuiz">重做</button>
          <button v-if="isViewingWrongOnly" class="btn secondary sm" @click="resetWrongQuestions">重刷错题</button>
        </template>
      </div>
    </div>

    <!-- Export Modal -->
    <div v-if="showExportModalFlag" class="modal-overlay" @click="closeExportModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header" >
          <h3>导出/分享试卷</h3>
          <button class="modal-close" @click="closeExportModal">×</button>
        </div>
        <div class="modal-body">
          <div class="modal-actions">
            <button class="btn secondary sm" @click="selectAllQuizzes">全选</button>
            <button class="btn secondary sm" @click="deselectAllQuizzes">取消全选</button>
          </div>
          <div class="quiz-list">
            <div v-for="quiz in reversedHistory" :key="quiz.id" class="quiz-item-checkbox">
              <input
                  type="checkbox"
                  :id="`quiz-${quiz.id}`"
                  :checked="selectedQuizzes.includes(quiz.id)"
                  @change="toggleQuizSelection(quiz.id)"
              >
              <label :for="`quiz-${quiz.id}`">
                <div class="quiz-info">
                  <div class="quiz-title">{{ quiz.title }}</div>
                  <div class="quiz-meta">
                    <span>{{ formatDate(quiz.timestamp) }}</span>
                    <span v-if="quiz.isSubmitted" class="score-info">{{ getQuizScore(quiz) }}/{{ quiz.questions.length }}</span>
                  </div>
                </div>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn secondary" @click="closeExportModal">取消</button>
          <button class="btn" @click="confirmExport" :disabled="selectedQuizzes.length === 0">确认导出</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useUserStore } from '../../api/user';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const router = useRouter();

// === 常量与状态 ===
const STORAGE_KEY = 'quiz_tool_history_v2';
const quizHistory = ref([]);
const quizGroups = ref([]); // 新增：分组列表
const currentQuizId = ref(null);
const isViewingWrongOnly = ref(false);
const leftSidebarCollapsed = ref(false);
const rightSidebarCollapsed = ref(false);
const isDark = ref(false);
const htmlInput = ref('');
const parseError = ref('');
const isCreating = ref(false);
const isMobile = ref(false); // 新增：移动端状态检测
const currentRetryWrongQuestionIds = ref(new Set()); // 追踪当前重试会话的错题ID
const currentWrongQuestionIds = ref(new Set()); // 追踪当前错题本中的题目ID
const draggedItem = ref(null); // 新增：拖拽的项目
const draggedItemType = ref(null); // 新增：拖拽的项目类型 ('quiz' 或 'group')

// 自动滚题相关状态
const isAutoScroll = ref(true); // 自动滚题开关，默认开启
const showNextButton = ref(false); // 下一题按钮显示状态
const currentQuestionIndex = ref(0); // 当前题目索引
const showMultiChoiceHint = ref(false); // 多选题提示显示状态
const quizMode = ref('scroll'); // 答题模式：'scroll'滚动模式，'single'单题模式

// Export Modal State
const showExportModalFlag = ref(false);
const selectedQuizzes = ref([]);

// 卡片悬停状态
const hoveredQuizId = ref(null);

// === 计算属性 ===
const reversedHistory = computed(() => [...quizHistory.value].reverse());
const wrongHistoryItems = computed(() => {
  return reversedHistory.value
      .filter(quiz => quiz.isSubmitted)
      .map(quiz => {
        const wrongCount = quiz.questions.filter(q => !checkAnswer(q)).length;
        return { ...quiz, wrongCount };
      })
      .filter(item => item.wrongCount > 0);
});
const currentQuiz = computed(() => quizHistory.value.find(q => q.id === currentQuizId.value) || null);
const questionsToShow = computed(() => {
  if (!currentQuiz.value) return [];
  if (isViewingWrongOnly.value) {
    if (!currentQuiz.value.isSubmitted && currentRetryWrongQuestionIds.value.size > 0) {
      // 重试会话中，显示原始错题列表
      return currentQuiz.value.questions.filter(q => currentRetryWrongQuestionIds.value.has(q.id));
    } else {
      // 错题本模式，显示所有在错题本中的题目（无论当前答案是否正确）
      return currentQuiz.value.questions.filter(q => currentWrongQuestionIds.value.has(q.id));
    }
  }
  return currentQuiz.value.questions;
});
const currentScore = computed(() => {
  if (!currentQuiz.value) return 0;
  return currentQuiz.value.questions.filter(q => checkAnswer(q)).length;
});
const currentTotal = computed(() => currentQuiz.value ? currentQuiz.value.questions.length : 0);
const displayedQuestions = computed(() => {
  if (quizMode.value === 'single') {
    // 单题模式下只返回当前索引的题目
    const q = questionsToShow.value[currentQuestionIndex.value];
    return q ? [q] : [];
  }
  // 滚动模式下返回所有题目
  return questionsToShow.value;
});

// === 生命周期与持久化 ===
onMounted(async () => {
  // 检查登录状态
  await userStore.initUser();
  if (!userStore.isLogin) {
    router.push('/');
    return;
  }
  
  loadHistory();
  loadGroups(); // 新增：加载分组数据
  applyThemeFromStorage();
  loadAutoScrollPreference();
  checkMobile();
  window.addEventListener('resize', checkMobile);

  // 移动端默认收起侧边栏
  if (window.innerWidth <= 768) {
    leftSidebarCollapsed.value = true;
    rightSidebarCollapsed.value = true;
  }
});

function loadAutoScrollPreference() {
  const savedPreference = localStorage.getItem('user_pref_auto_scroll');
  if (savedPreference !== null) {
    isAutoScroll.value = savedPreference === 'true';
  }
}

function toggleAutoScroll() {
  localStorage.setItem('user_pref_auto_scroll', isAutoScroll.value);
  // 切换开关时，根据当前题目类型更新按钮显示状态
  if (currentQuiz.value && questionsToShow.value.length > 0) {
    const currentQuestion = questionsToShow.value[currentQuestionIndex.value];
    if (!isAutoScroll.value || currentQuestion.type === 'multiple') {
      showNextButton.value = true;
    } else {
      showNextButton.value = false;
    }
  }
}

function toggleQuizMode() {
  quizMode.value = quizMode.value === 'scroll' ? 'single' : 'scroll';
  currentQuestionIndex.value = 0; // 切换模式时重置当前题目索引
  showNextButton.value = false; // 重置按钮状态
  window.scrollTo({ top: 0, behavior: 'smooth' }); // 滚动到顶部
}

// 新增：创建新分组
function createNewGroup() {
  const groupName = prompt("请输入分组名称:");
  if (groupName && groupName.trim()) {
    const newGroup = {
      id: Date.now().toString(),
      name: groupName.trim(),
      quizIds: [], // 分组内的试卷ID列表
      isExpanded: true, // 分组默认展开
      timestamp: Date.now()
    };
    quizGroups.value.push(newGroup);
    saveGroups();
  }
}

// 新增：保存分组到本地存储
function saveGroups() {
  localStorage.setItem('quiz_tool_groups_v1', JSON.stringify(quizGroups.value));
}

// 新增：从本地存储加载分组
function loadGroups() {
  const savedGroups = localStorage.getItem('quiz_tool_groups_v1');
  if (savedGroups) {
    try {
      quizGroups.value = JSON.parse(savedGroups);
    } catch (e) {
      console.error("加载分组失败", e);
      quizGroups.value = [];
    }
  }
}

// 新增：展开/折叠分组
function toggleGroupExpanded(groupId) {
  const group = quizGroups.value.find(g => g.id === groupId);
  if (group) {
    group.isExpanded = !group.isExpanded;
    saveGroups();
  }
}

// 新增：重命名分组
function renameGroup(groupId) {
  const group = quizGroups.value.find(g => g.id === groupId);
  if (!group) return;
  const newName = prompt("请输入新的分组名称:", group.name);
  if (newName && newName.trim() !== group.name) {
    group.name = newName.trim();
    saveGroups();
  }
}

// 新增：删除分组
function deleteGroup(groupId) {
  if (!confirm("确定要删除这个分组吗？分组内的试卷不会被删除。")) return;
  quizGroups.value = quizGroups.value.filter(g => g.id !== groupId);
  saveGroups();
}

// 新增：拖拽相关函数
function handleDragStart(event, item, type) {
  draggedItem.value = item;
  draggedItemType.value = type;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', item.id);
  // 添加拖拽样式
  if (event.currentTarget) {
    event.currentTarget.classList.add('dragging');
  }
}

function handleDragOver(event) {
  event.preventDefault();
  event.dataTransfer.dropEffect = 'move';
}

function handleDragEnter(event) {
  event.preventDefault();
  // 高亮分组作为放置区域
  const dropZone = event.currentTarget;
  if (dropZone) {
    dropZone.classList.add('drop-zone');
  }
}

function handleDragLeave(event) {
  // 移除高亮样式
  const dropZone = event.currentTarget;
  if (dropZone) {
    dropZone.classList.remove('drop-zone');
  }
}

function handleDrop(event, groupId) {
  event.preventDefault();
  
  // 移除高亮样式
  const dropZone = event.currentTarget;
  if (dropZone) {
    dropZone.classList.remove('drop-zone');
  }
  
  if (!draggedItem.value || draggedItemType.value !== 'quiz') return;
  
  // 将试卷添加到分组
  const group = quizGroups.value.find(g => g.id === groupId);
  if (group && !group.quizIds.includes(draggedItem.value.id)) {
    group.quizIds.push(draggedItem.value.id);
    saveGroups();
  }
  
  // 清除拖拽状态
  draggedItem.value = null;
  draggedItemType.value = null;
  if (event.currentTarget) {
    event.currentTarget.classList.remove('dragging');
  }
}

function handleDragEnd(event) {
  // 清除拖拽样式
  if (event.currentTarget) {
    event.currentTarget.classList.remove('dragging');
  }
  draggedItem.value = null;
  draggedItemType.value = null;
}

// 新增：从分组中移除试卷
function removeQuizFromGroup(quizId, groupId) {
  const group = quizGroups.value.find(g => g.id === groupId);
  if (group) {
    group.quizIds = group.quizIds.filter(id => id !== quizId);
    saveGroups();
  }
}

// 新增：根据ID获取试卷
function getQuizById(quizId) {
  return quizHistory.value.find(quiz => quiz.id === quizId) || null;
}

// 新增：获取未分组的试卷
const ungroupedQuizzes = computed(() => {
  // 获取所有已分组的试卷ID
  const groupedQuizIds = new Set();
  quizGroups.value.forEach(group => {
    group.quizIds.forEach(quizId => groupedQuizIds.add(quizId));
  });
  // 返回未分组的试卷
  return quizHistory.value.filter(quiz => !groupedQuizIds.has(quiz.id)).reverse();
});

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile);
});

watch(quizHistory, () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(quizHistory.value));
}, { deep: true });

function loadHistory() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    try {
      quizHistory.value = JSON.parse(stored);
    } catch (e) {
      console.error("Storage corrupted", e);
      quizHistory.value = [];
    }
  }
}
function saveHistory() { /* Vue Reactivity 自动处理 */ }

// === 移动端适配逻辑 ===
function checkMobile() {
  isMobile.value = window.innerWidth <= 768;
}

function toggleLeftSidebar() {
  leftSidebarCollapsed.value = !leftSidebarCollapsed.value;
  if (!leftSidebarCollapsed.value && isMobile.value) {
    rightSidebarCollapsed.value = true; // 互斥
  }
}

function toggleRightSidebar() {
  rightSidebarCollapsed.value = !rightSidebarCollapsed.value;
  if (!rightSidebarCollapsed.value && isMobile.value) {
    leftSidebarCollapsed.value = true; // 互斥
  }
}

function closeAllSidebars() {
  // 移除 isMobile 判断，让点击题目时在 PC 端也能自动收起侧边栏
  leftSidebarCollapsed.value = true;
  rightSidebarCollapsed.value = true;
}

// === 业务逻辑 ===
function createNewQuiz() {
  currentQuizId.value = null;
  htmlInput.value = '';
  parseError.value = '';
  isCreating.value = true;
  if(isMobile.value) closeAllSidebars();
}

function loadQuiz(id, wrongOnly) {
  currentQuizId.value = id;
  isViewingWrongOnly.value = wrongOnly;
  isCreating.value = false;
  currentQuestionIndex.value = 0; // 重置当前题目索引
  showNextButton.value = false; // 重置按钮状态
  currentRetryWrongQuestionIds.value.clear(); // 清除重试会话的错题ID列表
  
  // 加载错题本时，根据isWrong属性更新currentWrongQuestionIds
  if (wrongOnly && currentQuiz.value) {
    currentWrongQuestionIds.value = new Set(
      currentQuiz.value.questions.filter(q => q.isWrong).map(q => q.id)
    );
  } else {
    currentWrongQuestionIds.value.clear();
  }
  
  window.scrollTo({ top: 0, behavior: 'smooth' });
  if(isMobile.value) closeAllSidebars();
}

function renameQuiz(id) {
  const quiz = quizHistory.value.find(q => q.id === id);
  if (!quiz) return;
  const newName = prompt("请输入新的试卷名称:", quiz.title);
  if (newName && newName.trim() !== "") {
    quiz.title = newName.trim();
  }
}

function deleteQuiz(id) {
  if (!confirm("确定要永久删除这张试卷吗？")) return;
  quizHistory.value = quizHistory.value.filter(q => q.id !== id);
  
  // 从所有分组中移除被删除的试卷
  quizGroups.value.forEach(group => {
    group.quizIds = group.quizIds.filter(quizId => quizId !== id);
  });
  saveGroups();
  
  if (currentQuizId.value === id) {
    currentQuizId.value = null;
    isCreating.value = false;
  }
}

function submitQuiz() {
  if (currentQuiz.value) {
    // 标记错题状态
    currentQuiz.value.questions.forEach(q => {
      q.isWrong = !checkAnswer(q);
    });
    currentQuiz.value.isSubmitted = true;
    // 清除重试会话的错题ID列表，回到正常过滤逻辑
    currentRetryWrongQuestionIds.value.clear();
    showNextButton.value = false;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // 单题模式下提交后自动切换为滚动模式
    quizMode.value = 'scroll';
  }
}

function shuffleQuestions(questions) {
  for (let i = questions.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [questions[i], questions[j]] = [questions[j], questions[i]];
  }
}

function resetCurrentQuiz() {
  if (!confirm("确定要清空当前答案重新开始吗？")) return;
  if (currentQuiz.value) {
    currentQuiz.value.isSubmitted = false;
    currentQuiz.value.questions.forEach(q => q.userAnswer = '');
    isViewingWrongOnly.value = false;
    currentQuestionIndex.value = 0;
    showNextButton.value = false;
    shuffleQuestions(currentQuiz.value.questions);
  }
}

function resetWrongQuestions() {
  if (!currentQuiz.value || !currentQuiz.value.isSubmitted) return;
  
  const wrongQuestions = currentQuiz.value.questions.filter(q => !checkAnswer(q));
  
  if (wrongQuestions.length === 0) {
    alert("当前没有错题需要重刷！");
    return;
  }
  
  if (!confirm(`确定要重新刷这 ${wrongQuestions.length} 道错题吗？`)) return;
  
  // 保存原始错题ID列表
  currentRetryWrongQuestionIds.value = new Set(wrongQuestions.map(q => q.id));
  
  currentQuiz.value.isSubmitted = false;
  // 只重置错题的答案
  wrongQuestions.forEach(q => q.userAnswer = '');
  // 设置为只看错题模式
  isViewingWrongOnly.value = true;
  currentQuestionIndex.value = 0;
  showNextButton.value = false;
  // 不需要打乱所有问题，因为 isViewingWrongOnly 会自动过滤出错题
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 辅助逻辑
function checkAnswer(q) {
  if (q.type === 'single') {
    return q.userAnswer === q.correctAnswer;
  } else if (q.type === 'multiple') {
    const sortStr = (str) => (str || '').split(',').filter(s=>s).sort().join(',');
    return sortStr(q.userAnswer) === sortStr(q.correctAnswer);
  } else {
    const cleanUser = (q.userAnswer || "").replace(/\s+/g, '').toLowerCase();
    const cleanCorrect = (q.correctAnswer || "").replace(/\s+/g, '').toLowerCase();
    return cleanCorrect.length > 0 && cleanUser === cleanCorrect;
  }
}

function removeFromWrongQuestions(questionId) {
  if (!currentQuiz.value) return;
  
  // 从currentWrongQuestionIds中移除
  currentWrongQuestionIds.value.delete(questionId);
  
  // 更新对应问题的isWrong属性
  const question = currentQuiz.value.questions.find(q => q.id === questionId);
  if (question) {
    question.isWrong = false;
  }
  
  // 如果错题本为空，显示提示
  if (currentWrongQuestionIds.value.size === 0) {
    setTimeout(() => {
      alert("错题本已清空！");
    }, 500);
  }
}

function formatDate(ts) {
  // 移动端简化日期显示
  const date = new Date(ts);
  if (isMobile.value) {
    return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2,'0')}`;
  }
  return date.toLocaleString();
}

function getQuizScore(quiz) {
  return quiz.questions.filter(q => checkAnswer(q)).length;
}

function getScoreClass(quiz) {
  const score = getQuizScore(quiz);
  const total = quiz.questions.length;
  return score === total ? 'good' : 'bad';
}

function getTypeLabel(type) {
  if (type === 'single') return '单选'; // 简化文字
  if (type === 'multiple') return '多选';
  return '简答';
}

function isCheckboxChecked(q, label) {
  const set = (q.userAnswer || '').split(',');
  return set.includes(label);
}

function toggleCheckbox(q, label, checked) {
  let set = (q.userAnswer || '').split(',').filter(s => s);
  if (checked) {
    if (!set.includes(label)) set.push(label);
  } else {
    set = set.filter(v => v !== label);
  }
  q.userAnswer = set.sort().join(',');
}

// 处理选项选择逻辑
function handleOptionSelect(q, index) {
  saveHistory();
  closeAllSidebars();
  
  // 更新当前题目索引 - 在单题模式下需要找到实际在 questionsToShow 中的索引
  if (quizMode.value === 'single') {
    const actualIndex = questionsToShow.value.findIndex(item => item.id === q.id);
    if (actualIndex !== -1) {
      currentQuestionIndex.value = actualIndex;
    }
  } else {
    currentQuestionIndex.value = index;
  }
  
  // 多选题提示
  if (q.type === 'multiple' && isAutoScroll.value && !showMultiChoiceHint.value) {
    showMultiChoiceHint.value = true;
    // 3秒后自动隐藏提示
    setTimeout(() => {
      showMultiChoiceHint.value = false;
    }, 3000);
  }
  
  // 单题模式下不自动跳转，始终显示下一题按钮
  if (quizMode.value === 'single') {
    showNextButton.value = true;
    return;
  }
  
  // 判断是否触发自动滚题
  // 核心逻辑：开关必须开启 && 必须不是多选题
  const shouldAutoScroll = isAutoScroll.value && q.type !== 'multiple';
  
  if (shouldAutoScroll) {
    // 优化体验：增加短暂延迟，让用户看清自己选了什么
    setTimeout(() => {
      goToNextQuestion();
    }, 300); // 300ms 延迟最佳
  } else {
    // 如果不自动跳，确保"下一题"按钮是可见的
    showNextButton.value = true;
  }
}

// 跳转到上一题
function goToPreviousQuestion() {
  if (!currentQuiz.value) return;
  
  const prevIndex = currentQuestionIndex.value - 1;
  
  if (prevIndex >= 0) {
    // 有上一题，更新当前题目索引
    currentQuestionIndex.value = prevIndex;
  }
}

// 跳转到下一题
function goToNextQuestion() {
  if (!currentQuiz.value) return;
  
  const totalQuestions = questionsToShow.value.length;
  const nextIndex = currentQuestionIndex.value + 1;
  
  if (nextIndex < totalQuestions) {
    // 有下一题，更新当前题目索引
    currentQuestionIndex.value = nextIndex;
    
    // 滚动模式下才需要滚动到下一题
    if (quizMode.value === 'scroll') {
      scrollToQuestion(nextIndex);
    }
    
    showNextButton.value = false; // 重置按钮状态
  } else {
    // 没有下一题，检查是否需要提交
    if (!currentQuiz.value.isSubmitted) {
      // 自动提交，submitQuiz 函数会自动切换到滚动模式
      submitQuiz();
    }
    showNextButton.value = false;
  }
}

function scrollToQuestion(index) {
  // 建议给每个题目加个 id，比 nth-child 更稳定，例如 id="question-0"
  const questionElement = document.querySelector(`.question-card:nth-child(${index + 1})`);

  if (questionElement) {
    questionElement.scrollIntoView({
      behavior: 'smooth',
      block: 'center', // 关键修改：start -> center (垂直居中)
      inline: 'nearest'
    });
  }
}

function showDemoHelp() {
  alert("请复制题目网页的 HTML 源码粘贴到输入框中。");
}

// === Export Modal Functions ===
function showExportModal() {
  showExportModalFlag.value = true;
  selectedQuizzes.value = [];
}

function closeExportModal() {
  showExportModalFlag.value = false;
  selectedQuizzes.value = [];
}

function selectAllQuizzes() {
  selectedQuizzes.value = quizHistory.value.map(quiz => quiz.id);
}

function deselectAllQuizzes() {
  selectedQuizzes.value = [];
}

function toggleQuizSelection(quizId) {
  const index = selectedQuizzes.value.indexOf(quizId);
  if (index > -1) {
    selectedQuizzes.value.splice(index, 1);
  } else {
    selectedQuizzes.value.push(quizId);
  }
}

function confirmExport() {
  if (selectedQuizzes.value.length === 0) return;
  
  // Gather selected quizzes
  const selectedQuizObjects = quizHistory.value.filter(quiz => 
    selectedQuizzes.value.includes(quiz.id)
  );
  
  // Generate JSON string
  const jsonContent = JSON.stringify(selectedQuizObjects, null, 2);
  
  // Create download link
  const blob = new Blob([jsonContent], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  
  // Generate filename with date
  const date = new Date();
  const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  a.download = `quiz-export-${dateStr}.json`;
  a.href = url;
  a.click();
  
  // Cleanup
  URL.revokeObjectURL(url);
  
  // Close modal
  closeExportModal();
}

// === 主题切换 ===
function applyThemeFromStorage() {
  const theme = localStorage.getItem('theme');
  isDark.value = theme === 'dark';
  if (isDark.value) {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
}

function toggleTheme(event) {
  const switchThemeLogic = () => {
    isDark.value = !isDark.value;
    if (isDark.value) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
  };
  if (!document.startViewTransition) {
    switchThemeLogic();
    return;
  }
  const x = event ? event.clientX : window.innerWidth / 2;
  const y = event ? event.clientY : 60;
  const endRadius = Math.hypot(
      Math.max(x, window.innerWidth - x),
      Math.max(y, window.innerHeight - y)
  );
  const transition = document.startViewTransition(switchThemeLogic);
  transition.ready.then(() => {
    document.documentElement.animate(
        { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${endRadius}px at ${x}px ${y}px)`] },
        { duration: 400, easing: 'ease-in', pseudoElement: '::view-transition-new(root)' }
    );
  });
}

// 🆕 新增：处理文件上传
function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  // 限制文件大小 (例如 10MB)
  if (file.size > 10 * 1024 * 1024) {
    alert("文件过大，请直接复制内容粘贴");
    return;
  }

  const reader = new FileReader();

  reader.onload = (e) => {
    try {
      // 检查是否为 JSON 文件
      if (file.name.endsWith('.json')) {
        const jsonContent = e.target.result;
        const importedQuizzes = JSON.parse(jsonContent);
        
        // 验证数据格式
        if (!Array.isArray(importedQuizzes)) {
          throw new Error('JSON 文件格式错误：必须是试卷数组');
        }
        
        // 合并到历史记录
        mergeImportedQuizzes(importedQuizzes);
        
        // 显示成功消息
        alert(`成功导入 ${importedQuizzes.length} 个试卷`);
      } else {
        // 非 JSON 文件，按原逻辑处理
        htmlInput.value = e.target.result;
      }
      
      // 清空错误信息
      parseError.value = '';
    } catch (error) {
      parseError.value = "解析错误: " + error.message;
      alert("文件解析失败: " + error.message);
    } finally {
      // 清空 input 使得同一个文件可以重复选择
      event.target.value = '';
    }
  };

  reader.onerror = () => {
    alert("读取文件失败");
  };

  // 默认使用 UTF-8 读取
  reader.readAsText(file, 'UTF-8');
}

function mergeImportedQuizzes(importedQuizzes) {
  // Get existing quiz IDs to check for duplicates
  const existingIds = new Set(quizHistory.value.map(quiz => quiz.id));
  let lastImportedQuizId = null;
  
  importedQuizzes.forEach(quiz => {
    // Validate required fields
    if (!quiz.title || !Array.isArray(quiz.questions)) {
      console.warn('Skipping invalid quiz:', quiz);
      return;
    }
    
    // Handle duplicate IDs
    let quizId = quiz.id;
    if (existingIds.has(quizId)) {
      // Generate new ID if duplicate
      quizId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
      quiz.id = quizId;
    }
    
    // Ensure all required fields are present
    if (!quiz.timestamp) {
      quiz.timestamp = Date.now();
    }
    
    if (quiz.isSubmitted === undefined) {
      quiz.isSubmitted = false;
    }
    
    // Add to history
    quizHistory.value.push(quiz);
    existingIds.add(quizId);
    lastImportedQuizId = quizId;
  });
  
  // 自动加载最后导入的试卷
  if (lastImportedQuizId) {
    loadQuiz(lastImportedQuizId, false);
  }
}
// === 解析核心逻辑 ===
function parseAndGenerate() {
  const input = htmlInput.value;
  if (!input.trim()) return;
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(input, 'text/html');
    let questions = [];
    // 1. 尝试常规格式
    let listItems = doc.querySelectorAll('.studentTestDetail-list');
    if (listItems.length === 0) {
      const plugins = doc.querySelectorAll('[class*="plugins-testType-"]');
      if (plugins.length > 0) listItems = plugins;
    }
    if (listItems.length === 0) {
      const boxes = doc.querySelectorAll('.content-box');
      if (boxes.length > 0) listItems = Array.from(boxes).map(b => b.parentElement.parentElement);
    }
    if (listItems.length > 0) {
      questions = parseStandardQuiz(listItems);
    } else {
      // 2. 尝试 Angular/MOOC 格式
      const angularItems = doc.querySelectorAll('app-object-quiz-item');
      if (angularItems.length > 0) {
        questions = parseAngularQuiz(doc);
      }
    }
    if (questions.length === 0) throw new Error("未识别到题目结构");
    // 强制清空答案
    questions.forEach(q => q.userAnswer = '');
    const newQuiz = {
      id: Date.now().toString(),
      timestamp: Date.now(),
      title: `试卷 ${new Date().toLocaleTimeString()}`,
      questions: questions,
      isSubmitted: false
    };
    quizHistory.value.push(newQuiz);
    loadQuiz(newQuiz.id, false);
    isCreating.value = false;
    parseError.value = '';
  } catch (e) {
    console.error(e);
    parseError.value = "解析错误: " + e.message;
  }
}

function fixHtmlContent(html) {
  if (!html) return '';
  let content = html.replace(/src="\/\//g, 'src="https://');
  content = content.replace(/<img /g, '<img referrerpolicy="no-referrer" ');
  return content;
}

// 解析器: Angular/MOOC
function parseAngularQuiz(doc) {
  const items = doc.querySelectorAll('app-object-quiz-item');
  const results = [];
  items.forEach((item, index) => {
    const q = {
      id: index,
      type: 'unknown',
      content: '',
      options: [],
      correctAnswer: '',
      userAnswer: '',
      explanation: ''
    };
    const body = item.querySelector('.question-body');
    if (body) q.content = fixHtmlContent(body.innerHTML);
    const radioGroup = item.querySelector('nz-radio-group');
    const checkboxGroup = item.querySelector('nz-checkbox-wrapper');
    const optionsContainer = radioGroup || checkboxGroup;
    if (checkboxGroup) q.type = 'multiple';
    else if (radioGroup) q.type = 'single';
    else q.type = 'text';
    if (optionsContainer) {
      const labels = optionsContainer.querySelectorAll('label');
      labels.forEach(lbl => {
        const spans = lbl.querySelectorAll('span');
        let text = '';
        spans.forEach(s => {
          if (!s.className.includes('ant-radio') && !s.className.includes('ant-checkbox')) {
            text = s.innerHTML.trim();
          }
        });
        if (!text) text = lbl.innerText.trim();
        const match = text.match(/^([A-Z])\.\s*(.*)/);
        let label, html;
        if (match) {
          label = match[1];
          html = match[2];
        } else {
          label = text;
          html = text;
        }
        q.options.push({ label: label, html: html });
      });
    }
    const ansDiv = item.querySelector('.correct-answer');
    if (ansDiv) {
      let ansText = ansDiv.innerText.replace('正确答案:', '').trim();
      ansText = ansText.replace(/，/g, ',');
      if (q.type === 'multiple') ansText = ansText.replace(/\s+/g, '');
      q.correctAnswer = ansText;
    }
    if (!q.correctAnswer) {
      const resultCorrect = item.querySelector('.result-correct');
      if (resultCorrect) {
        q.correctAnswer = q.userAnswer;
      }
    }
    const knowledgeNode = item.querySelector('.knowledge-points .item-title');
    if (knowledgeNode) {
      q.explanation = knowledgeNode.innerText.trim();
    } else {
      const kp = item.querySelector('.knowledge-points');
      if (kp) {
        let text = kp.innerText.trim();
        if (text.startsWith("答案解析")) text = text.substring(4).trim();
        q.explanation = text;
      }
    }
    results.push(q);
  });
  return results;
}

// 解析器: 常规
function parseStandardQuiz(listItems) {
  const results = [];
  listItems.forEach((item, index) => {
    const q = { id: index, type: 'unknown', content: '', options: [], correctAnswer: '', userAnswer: '', explanation: '' };
    let mainContainer = item;
    if (!item.className || !item.className.includes('plugins-testType-')) {
      const found = item.querySelector('[class*="plugins-testType-"]');
      if (found) mainContainer = found;
    }
    const contentBox = mainContainer.querySelector('.content-box');
    if (contentBox) q.content = fixHtmlContent(contentBox.innerHTML);
    else return;
    const descDiv = mainContainer.querySelector('.desc');
    if (descDiv) q.meta = descDiv.innerText;
    const radioGroup = mainContainer.querySelector('.SingleChoice-radio') || mainContainer.querySelector('.el-radio-group');
    if (radioGroup) {
      q.type = 'single';
      const radios = radioGroup.querySelectorAll('label');
      radios.forEach(radio => {
        const choiceSpan = radio.querySelector('.choice');
        if (choiceSpan) {
          const letter = (choiceSpan.innerText.trim().match(/^([A-Z])\./) || [null, '?'])[1];
          const contentDiv = choiceSpan.querySelector('div');
          const html = contentDiv ? fixHtmlContent(contentDiv.innerHTML) : choiceSpan.innerText.replace(/^[A-Z]\./, '');
          q.options.push({ label: letter, html: html });
        }
      });
      const correctNode = mainContainer.querySelector('.answer-correct-type i');
      if (correctNode) q.correctAnswer = correctNode.innerText.trim();
    } else {
      q.type = 'text';
      let foundAns = false;
      const refNames = mainContainer.querySelectorAll('.reference-name');
      refNames.forEach(nameNode => {
        if (nameNode.innerText.includes('参考答案')) {
          const cont = nameNode.parentElement.querySelector('.reference-cont');
          if (cont) {
            q.correctAnswer = cont.innerText.trim();
            foundAns = true;
          }
        }
      });
      if (!foundAns) {
        const correctNode = mainContainer.querySelector('.answer-correct-type i');
        if (correctNode) q.correctAnswer = correctNode.innerText.trim();
      }
    }
    const analysisNode = mainContainer.querySelector('.analysisDesc');
    if (analysisNode) {
      q.explanation = analysisNode.innerText.replace('试题解析', '').trim();
    }
    results.push(q);
  });
  return results;
}
</script>
<style>
/* 定义全局变量，确保样式穿透 */
:root {
  --primary: #007AFF;
  --primary-hover: #0056CC;
  --success: #34C759;
  --danger: #FF3B30;
  --warning: #FF9500;
  --bg: #F2F2F7;
  --card-bg: #FFFFFF;
  --text: #1C1C1E;
  --text-secondary: #636366;
  --text-light: #8E8E93;
  --border: #E5E5EA;
  --border-light: #F0F0F5;
  --input-bg: #F2F2F7;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.15);
  --sidebar-width: 350px;
  --header-height: 80px;

  /* 滚动条专用变量 (浅色模式) */
  --scrollbar-track: transparent;
  --scrollbar-thumb: #C7C7CC;
  --scrollbar-thumb-hover: #AEAEB2;
  --scrollbar-width: 8px;
}
/* Dark Mode 适配 */
[data-theme="dark"] {
  --primary: #0A84FF;
  --primary-hover: #0066CC;
  --success: #30D158;
  --danger: #FF453A;
  --warning: #FF9F0A;
  --bg: #000000;
  --card-bg: #1C1C1E;
  --text: #FFFFFF;
  --text-secondary: #8E8E93;
  --text-light: #636366;
  --border: #2C2C2E;
  --border-light: #38383A;
  --input-bg: #2C2C2E;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 4px 12px rgba(0, 0, 0, 0.5);

  /* 滚动条专用变量 (深色模式) */
  --scrollbar-track: transparent;
  --scrollbar-thumb: #48484A;
  --scrollbar-thumb-hover: #636366;
}
</style>

<style scoped>


/* === 🆕 优化后的滚动条样式 === */

/* Firefox 适配 */
:global(*) {
  scrollbar-width: thin;
  scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
}

/* Webkit (Chrome, Edge, Safari) 适配 */
:global(::-webkit-scrollbar) {
  width: var(--scrollbar-width);
  height: var(--scrollbar-width); /* 用于横向滚动条 */
}

:global(::-webkit-scrollbar-track) {
  background: var(--scrollbar-track);
  border-radius: 4px;
}

:global(::-webkit-scrollbar-thumb) {
  background-color: var(--scrollbar-thumb);
  border-radius: 99px; /*以此实现胶囊形状*/

  /* 核心技巧：使用透明边框挤压背景，使滚动条看起来更细，
     但鼠标感应区域依然保留原宽度，体验更好 */
  border: 3px solid transparent;
  background-clip: content-box;

  transition: background-color 0.3s ease;
}

:global(::-webkit-scrollbar-thumb:hover) {
  background-color: var(--scrollbar-thumb-hover);
  /* 悬停时稍微加粗一点点视觉效果（可选，保持边框不变则宽度不变） */
  border: 2px solid transparent;
}

/* 针对侧边栏等特定区域的微调 (可选) */
/* 如果希望侧边栏滚动条更隐蔽，可以单独设置 */
.sidebar-content::-webkit-scrollbar {
  width: 6px; /* 侧边栏稍细 */
}
.sidebar-content::-webkit-scrollbar-thumb {
  border: 1px solid transparent; /* 边框更细 */
}

/* 移动端适配：为侧边栏内容添加底部padding，避免被底部栏遮盖 */
@media (max-width: 768px) {
  .sidebar-content {
    padding-bottom: 80px; /* 大于底部栏高度 */
  }
}


/* 基础重置 */
.quiz-app-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 100;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 建立清晰的字体层次结构 */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.2;
  margin: 0;
  color: var(--text);
}

h1 {
  font-size: 1.5rem;
}

h2 {
  font-size: 1.375rem;
}

h3 {
  font-size: 1.25rem;
}

p, div, span, button {
  font-size: 1rem;
  line-height: 1.6;
}

/* 辅助文本样式 */
.text-secondary {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.text-sm {
  font-size: 0.875rem;
}

.text-xs {
  font-size: 0.75rem;
}

.app-brand h1, .quiz-title {
  font-family: 'Georgia', 'Cambria', serif;
  letter-spacing: 0.5px;
}

/* 头部样式 */
header {
  height: var(--header-height);
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  z-index: 60;
  gap: 20px;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.app-brand h1 {
  font-size: 1.3rem;
  margin: 0;
  white-space: nowrap;
  color: var(--text);
  font-weight: 600;
}

.quiz-header-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-left: 1px solid var(--border-light);
  padding-left: 20px;
  height: 40px;
  min-width: 0;
}

.quiz-info-group {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
  flex: 1;
  min-width: 0;
}

.quiz-title {
  font-weight: 500;
  font-size: 1.05em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
  max-width: 300px;
}

.quiz-action-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.score-board {
  font-weight: 600;
  color: var(--text);
  font-size: 1.05em;
  white-space: nowrap;
}

.score-highlight {
  color: var(--primary);
  font-weight: 700;
}

.divider {
  border-left: 1px solid var(--border-light);
  height: 24px;
}

/* 侧边栏优化 */
.sidebar {
  background-color: var(--card-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 350px !important;
  transition: all 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  z-index: 50;
}

.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

/* 移动端底部栏样式 */
.mobile-bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: var(--card-bg);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 60;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

/* 导入区域优化 */
.importer-section {
  background-color: var(--card-bg);
  padding: 24px;
  border-radius: 20px;
  box-shadow: var(--shadow);
  max-width: 850px;
  margin: 0 auto;
  width: 100%;
}

/* 移动端底部栏样式 */
.mobile-bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: var(--card-bg);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  z-index: 60;
}

.bottom-bar-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.bottom-bar-center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.bottom-bar-right {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: flex-end;
}

/* 头部操作区 */
.header-right-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.theme-toggle {
  background: var(--card-bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1.3rem;
  outline: none;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.icon-btn {
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 1.5rem;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 自动滚题开关样式 */
.auto-scroll-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 12px;
}

.toggle-label {
  font-size: 0.9rem;
  color: var(--text);
  white-space: nowrap;
  font-weight: 400;
}

/* 苹果风格开关 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 51px;
  height: 31px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--border);
  transition: all 0.2s ease;
  border-radius: 9999px;
  border: 1px solid transparent;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 25px;
  width: 25px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: all 0.2s ease;
  border-radius: 9999px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

input:checked + .toggle-slider {
  background-color: var(--primary);
}

input:checked + .toggle-slider:before {
  transform: translateX(20px);
}

input:focus + .toggle-slider {
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.2);
}

/* 表单元素优化 */
textarea {
  width: 100%;
  min-height: 150px;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background-color: var(--input-bg);
  color: var(--text);
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: var(--primary);
  background-color: var(--card-bg);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

/* 文件输入优化 */
input[type="file"] {
  opacity: 0;
  position: absolute;
  width: 0;
  height: 0;
}

label.upload-btn {
  cursor: pointer;
  transition: all 0.2s ease;
}

label.upload-btn:hover {
  transform: translateY(-1px);
}

label.upload-btn:active {
  transform: translateY(0);
}

/* 布局结构 */
.app-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
  min-height: 0;
}

/* 侧边栏通用样式 */
.sidebar {
  width: 350px !important;
  background-color: var(--card-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}
.right-sidebar {
  border-right: none;
  border-left: 1px solid var(--border);
}

.sidebar.collapsed {
  width: 0 !important;
  border: none;
}

.sidebar.collapsed .sidebar-content,
.sidebar.collapsed .sidebar-header {
  opacity: 0;
  pointer-events: none;
  overflow: hidden;
}

.sidebar-header {
  padding: 16px 20px;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  white-space: nowrap;
  color: var(--text);
  background-color: var(--card-bg);
  flex-shrink: 0;
  font-size: 1.1rem;
}
.new-quiz-btn {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
  transform-origin: right center;
  border-radius: 9999px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  min-height: 0;
  background-color: var(--card-bg);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border);
  background-color: var(--card-bg);
  flex-shrink: 0;
}

.export-btn {
  width: 100%;
  justify-content: center;
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
  border-radius: 9999px;
  font-size: 0.95rem;
  padding: 12px 20px;
  transition: all 0.2s ease;
}

.export-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.2);
}

.sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.sidebar-item {
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  border: 1px solid transparent;
  font-size: 0.9rem;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background-color: transparent;
  color: var(--text);
  display: flex;
  flex-direction: column;
  gap: 12px;
  -webkit-tap-highlight-color: transparent;
  margin-bottom: 0;
  height: auto;
  min-height: 120px;
  overflow: hidden;
  z-index: 1;
  align-items: center;
  text-align: center;
  transform-origin: top;
}

.sidebar-item * {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-item:hover {
  background-color: var(--card-bg);
  border-color: var(--border);
  box-shadow: var(--shadow);
  transform: translateY(-1px);
  height: auto;
  min-height: 120px;
}

.sidebar-item.active {
  background-color: var(--primary);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.2);
  height: auto;
  min-height: 120px;
}



.sidebar-item.active .date,
.sidebar-item.active .quiz-item-title {
  color: white;
}

.sidebar-item .date {
  font-size: 0.8rem;
  color: var(--text-secondary);
  display: block;
  margin: 0;
  font-weight: 400;
}

.wrong-count {
  color: var(--danger) !important;
  font-weight: 600;
}

.quiz-item-title {
  font-weight: 500;
  color: var(--text);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-tag {
  font-weight: 600;
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 9999px;
  background-color: var(--bg);
  white-space: nowrap;
  flex-shrink: 0;
}

.score-tag.good {
  color: var(--success);
  background-color: rgba(52, 199, 89, 0.1);
}

.score-tag.bad {
  color: var(--danger);
  background-color: rgba(255, 59, 48, 0.1);
}

.sidebar-actions {
  gap: 8px;
  padding: 0;
  margin-top: 8px;
  justify-content: center;
  background-color: transparent;
  border-radius: 0;
  border: none;
  backdrop-filter: none;
  display: flex;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 10px;
  border-radius: 8px;
  color: var(--text-secondary);
  min-width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  -webkit-tap-highlight-color: transparent;
  transform: scale(1);
}

.action-btn:hover {
  background-color: var(--primary);
  color: white;
  transform: scale(1.1);
}

.action-btn.delete:hover {
  background-color: var(--danger);
  transform: scale(1.1);
}

.sidebar-item.active .action-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.sidebar-item.active .action-btn.delete:hover {
  background-color: var(--danger);
}

/* 分组标题优化 */
.group-header {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  margin: 4px 8px;
  cursor: pointer;
  border-radius: 12px;
  transition: all 0.2s ease;
  font-weight: 500;
  gap: 8px;
}

.group-header:hover {
  background-color: var(--bg);
}

.group-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group-count {
  font-size: 0.8em;
  color: var(--text-secondary);
  font-weight: 400;
}

.group-actions {
  display: none;
  gap: 4px;
  margin-left: auto;
}

.group-header:hover .group-actions {
  display: flex;
}

/* 优化侧边栏头部按钮布局 */
.sidebar-header-buttons {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.sidebar-header-buttons .btn {
  padding: 6px 12px;
  font-size: 0.85em;
  min-height: auto;
}

.sidebar-toggle-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 48px;
  background-color: var(--card-bg);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 20;
  font-size: 12px;
  border-radius: 0 8px 8px 0;
}
.left-toggle { right: -24px; border-left: none; }
.right-toggle { left: -24px; border-right: none; border-radius: 8px 0 0 8px; }

/* 主内容区 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background-color: var(--bg);
  min-width: 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  -webkit-overflow-scrolling: touch; /* iOS 惯性滚动 */
  color: var(--text);
}

.container {
  max-width: 900px;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-height: 100%;
}

.quiz-area {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
/* 移动端底部留白防止遮挡 */
.pb-80 { padding-bottom: 80px; }

.importer-section {
  background: var(--card-bg);
  padding: 32px;
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
  margin-bottom: 32px;
  color: var(--text);
  width: 100%;
  max-width: 850px;
  box-sizing: border-box;
}

textarea {
  width: 100%;
  height: 180px;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  font-family: monospace;
  box-sizing: border-box;
  margin-bottom: 20px;
  resize: vertical;
  background-color: var(--input-bg);
  color: var(--text);
  font-size: 0.9em;
}
textarea:focus { outline: none; border-color: var(--primary); }

.btn-group { display: flex; gap: 12px; flex-wrap: wrap; }
.parse-error { color: var(--danger); margin-top: 12px; padding: 12px; background: rgba(239, 68, 68, 0.1); border-radius: 8px; }
.default-title { color: var(--text); text-align: center; margin: 60px 0; font-weight: 500; font-size: 1.4em; width: 100%; }
.empty-guide { text-align: center; margin-top: 40px; background-color: var(--card-bg); padding: 40px 20px; border-radius: 16px; box-shadow: var(--shadow); border: 1px solid var(--border); }

/* 侧边栏头部按钮样式 */
.sidebar-header-buttons {
  display: flex;
  gap: 8px;
}

.new-group-btn {
  background-color: var(--warning);
  border-color: var(--warning);
  color: white;
}

/* 分组样式 */
.sidebar-group {
  margin-bottom: 12px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
  background-color: var(--card-bg);
  transition: all 0.3s ease;
}

.sidebar-group:hover {
  box-shadow: var(--shadow);
}

/* 分组头部样式 */
.group-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--bg);
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid var(--border-light);
}

.group-header:hover {
  background-color: var(--input-bg);
}

.group-icon {
  margin-right: 8px;
  font-size: 0.7em;
  color: var(--text-secondary);
  transition: transform 0.3s ease;
}

.group-name {
  font-weight: 600;
  color: var(--text);
  flex: 1;
}

.group-count {
  font-size: 0.8em;
  color: var(--text-secondary);
  margin-right: 8px;
}

.group-actions {
  display: none;
  gap: 4px;
}

.group-header:hover .group-actions {
  display: flex;
}

/* 分组内试卷列表样式 */
.group-quizzes {
  list-style: none;
  padding: 0;
  margin: 0;
}

.group-quiz-item {
  margin: 4px 8px;
  border-color: var(--border-light);
  background-color: var(--input-bg);
}

.group-quiz-item:hover {
  border-color: var(--primary);
}

/* 未分组区域样式 */
.sidebar-group.ungrouped {
  margin-top: 16px;
  border-color: transparent;
  background-color: transparent;
}

.sidebar-group.ungrouped .group-header {
  background-color: transparent;
  border-bottom: none;
  padding: 0 8px;
}

/* 拖拽相关样式 */
.sidebar-item {
  cursor: grab;
  transition: all 0.3s ease;
}

.sidebar-item:active {
  cursor: grabbing;
}

.sidebar-item.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
  box-shadow: var(--shadow-lg);
}

.sidebar-group.drop-zone {
  background-color: rgba(74, 124, 89, 0.1);
  border-color: var(--primary);
}

/* 下一题按钮样式 */
.next-question-btn-container {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 600px;
  z-index: 50;
}

.next-btn {
  width: 100%;
  padding: 16px 24px;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 12px;
  background-color: var(--primary);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: var(--shadow-lg);
  transition: all 0.3s ease;
}

.next-btn:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
}

.next-btn:active {
  transform: translateY(0);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .next-question-btn-container {
    bottom: 15px;
    width: 95%;
  }
  
  .next-btn {
    padding: 14px 20px;
    font-size: 1rem;
  }
}

/* 多选题提示样式 */
.multi-choice-hint {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  animation: hint-slide-down 0.3s ease-out forwards;
}

.hint-content {
  background: var(--card-bg);
  color: var(--text);
  padding: 12px 20px;
  border-radius: 24px;
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--border);
}

.hint-icon {
  font-size: 1.2rem;
}

.hint-text {
  font-size: 0.9rem;
  font-weight: 500;
}

@keyframes hint-slide-down {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .multi-choice-hint {
    top: 70px;
  }
  
  .hint-content {
    padding: 10px 16px;
  }
  
  .hint-text {
    font-size: 0.85rem;
  }
}

/* 题目卡片 */
.question-card {
  background: var(--card-bg);
  padding: 24px;
  border-radius: 20px;
  box-shadow: var(--shadow);
  margin-bottom: 20px;
  border: 1px solid var(--border);
  border-left: 6px solid transparent;
  width: 100%;
  max-width: 850px;
  box-sizing: border-box;
  text-align: left;
  transition: all 0.3s ease;
}

.question-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.question-card.status-correct {
  border-left-color: var(--success);
  background-color: rgba(52, 199, 89, 0.05);
}

.question-card.status-wrong {
  border-left-color: var(--danger);
  background-color: rgba(255, 59, 48, 0.05);
}

.q-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 12px;
}

.remove-btn {
  font-size: 0.85em;
  padding: 6px 14px;
  white-space: nowrap;
}

.q-index {
  font-weight: 600;
  font-size: 1.1em;
  color: var(--text);
  flex: 1;
}

.q-content {
  font-size: 1.125em;
  margin-bottom: 20px;
  line-height: 1.6;
  color: var(--text);
}

:deep(.q-content img) {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  margin: 12px 0;
}

:deep(.q-content table) {
  width: 100%;
  overflow-x: auto;
  display: block;
  border-collapse: collapse;
  margin: 12px 0;
}

:deep(.q-content table th),
:deep(.q-content table td) {
  border: 1px solid var(--border);
  padding: 10px 12px;
  font-size: 0.9em;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.option-label {
  display: flex;
  align-items: flex-start;
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  cursor: pointer;
  background-color: var(--card-bg);
  color: var(--text);
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.option-label:hover {
  background-color: var(--bg);
  border-color: var(--primary);
  transform: translateY(-1px);
}

.option-label:active {
  transform: translateY(0);
}

.option-label input {
  margin-top: 4px;
  margin-right: 14px;
  accent-color: var(--primary);
  transform: scale(1.15);
}

.option-text {
  font-size: 1em;
  line-height: 1.5;
  color: var(--text);
  word-break: break-word;
  flex: 1;
}

/* 正确选项高亮 */
.option-label.correct-option {
  background-color: rgba(52, 199, 89, 0.05);
  border-color: var(--success);
}

/* 单题模式优化 */
.question-card.single-mode {
  margin-bottom: 0;
}

/* 短答案输入框优化 */
.short-answer-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background-color: var(--input-bg);
  color: var(--text);
  font-size: 1em;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.short-answer-input:focus {
  outline: none;
  border-color: var(--primary);
  background-color: var(--card-bg);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

/* 结果分析区域优化 */
.result-analysis {
  background-color: var(--bg);
  padding: 16px;
  border-radius: 12px;
  margin-top: 16px;
}

.result-analysis p {
  margin: 8px 0;
}

.result-analysis strong {
  font-weight: 600;
}

.explanation-box {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

.explanation-box strong {
  display: block;
  margin-bottom: 8px;
}

/* 正确选项的绿色样式 */
.correct-option {
  background-color: rgba(16, 185, 129, 0.1);
  border-color: var(--success);
  border-left: 4px solid var(--success);
}
.option-text b { color: var(--primary); font-weight: 600; margin-right: 4px; }

.short-answer-input {
  width: 100%;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  font-size: 1rem;
  background-color: var(--input-bg);
  color: var(--text);
}
.short-answer-input:focus { outline: none; border-color: var(--primary); }

.result-analysis { margin-top: 24px; padding-top: 24px; border-top: 1px dashed var(--border); }
.result-analysis p { margin: 12px 0; display: flex; align-items: flex-start; gap: 12px; color: var(--text); }
.break-word { word-break: break-all; }
.explanation-box { margin-top: 20px; padding: 20px; background-color: var(--bg); border-radius: 12px; color: var(--text-secondary); font-size: 0.95em; }

.tag { display: inline-block; padding: 6px 12px; border-radius: 8px; font-size: 0.8em; font-weight: 600; margin-right: 8px; white-space: nowrap; flex-shrink: 0; }
.tag.correct-ans { background: rgba(16, 185, 129, 0.15); color: var(--success); }
.tag.wrong-ans { background: rgba(239, 68, 68, 0.15); color: var(--danger); }
.tag.type { background: var(--primary); color: white; }
.tag.mode-badge { background: var(--danger); color: white; padding: 2px 6px; font-size: 0.75em; }

.btn {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 9999px;
  cursor: pointer;
  font-size: 0.95em;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 36px;
  min-width: 44px;
  -webkit-tap-highlight-color: transparent;
}

.btn:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.btn:active {
  transform: translateY(0);
}

.btn.secondary {
  background-color: var(--border);
  color: var(--text);
}

.btn.secondary:hover {
  background-color: var(--border-light);
}

.btn.sm {
  padding: 6px 14px;
  font-size: 0.875em;
  min-height: 30px;
}

.btn.full-width {
  width: 100%;
  padding: 12px 20px;
  font-size: 1em;
  min-height: 44px;
}

.btn.active {
  background-color: var(--primary);
  color: white;
}

.shadow-btn {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

/* 图标按钮优化 */
.icon-btn {
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 1.5rem;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  transition: all 0.2s ease;
  min-width: 44px;
  min-height: 44px;
  -webkit-tap-highlight-color: transparent;
}

.icon-btn:hover {
  background-color: var(--border-light);
}

.icon-btn:active {
  background-color: var(--border);
}

/* 主题切换按钮优化 */
.theme-toggle {
  background: var(--card-bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 8px;
  border-radius: 9999px;
  cursor: pointer;
  font-size: 1.3rem;
  outline: none;
  transition: all 0.2s ease;
  min-width: 44px;
  min-height: 44px;
  -webkit-tap-highlight-color: transparent;
}

.theme-toggle:hover {
  background-color: var(--border-light);
  border-color: var(--border-light);
}

.theme-toggle:active {
  background-color: var(--border);
}

/* 动画和过渡效果 */

/* 渐入动画 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 滑入动画 */
@keyframes slideInFromLeft {
  from { transform: translateX(-100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes slideInFromRight {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

/* 淡入淡出动画 */
@keyframes fadeInOut {
  0%, 100% { opacity: 0; }
  50% { opacity: 1; }
}

/* 弹性动画 */
@keyframes bounceIn {
  0% { transform: scale(0.9); opacity: 0; }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}

/* 移动端遮罩 */
.mobile-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 40;
  backdrop-filter: blur(2px);
  animation: fadeIn 0.3s ease;
}

/* 侧边栏动画 */
.sidebar {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.mobile-open {
  animation: slideInFromLeft 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.right-sidebar.mobile-open {
  animation: slideInFromRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 题目卡片动画 */
.question-card {
  animation: fadeIn 0.3s ease;
}

/* 模态框动画 */
.modal-overlay {
  animation: fadeIn 0.3s ease;
}

.modal-content {
  animation: slideInFromBottom 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideInFromBottom {
  from { transform: translateY(50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* 选项动画 */
.option-label {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 按钮动画 */
.btn {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 分组展开/折叠动画 */
.group-header:not(.expanded) + .group-quizzes {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.group-header {
  transition: all 0.2s ease;
}

/* 多选提示动画 */
.multi-choice-hint {
  animation: slideInFromTop 0.3s ease;
}

@keyframes slideInFromTop {
  from { transform: translateY(-100%); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* 加载状态动画 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.loading {
  animation: pulse 1.5s infinite;
}

/* 单题模式样式 */
.question-progress {
  display: block;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 auto;
  color: white;
  background-color: var(--danger);
  padding: 10px 40px;
  border-radius: 9999px;
  text-align: center;
  width: fit-content;
  box-sizing: border-box;
  position: relative;
  z-index: 2;
}

.progress-fade-enter-active,
.progress-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-fade-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(-10px);
}

.progress-fade-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(-10px);
}

.progress-fade-enter-to,
.progress-fade-leave-from {
  opacity: 1;
  transform: scale(1) translateY(0);
}

.actions-slide-enter-active,
.actions-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.actions-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
  max-height: 0;
}

.actions-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
  max-height: 0;
}

.actions-slide-enter-to,
.actions-slide-leave-from {
  opacity: 1;
  transform: translateY(0);
  max-height: 50px;
  margin-top: 12px;
}

.single-mode-nav-btns {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  gap: 16px;
}

.single-mode-nav-btns .prev-btn {
  width: auto;
  padding: 12px 24px;
  font-size: 1rem;
}

.single-mode-nav-btns .next-btn {
  width: auto;
  padding: 12px 24px;
  font-size: 1rem;
}

.question-card.single-mode {
  margin: 0 auto;
  max-width: 850px;
}

/* ==========================================================================
   移动端响应式样式 (Max Width 768px)
   ========================================================================== */
@media (max-width: 768px) {
  :global(:root) {
    --header-height: 56px;
    --sidebar-width: 60%; /* 侧边栏占屏幕宽度的 85% */
  }

  /* 头部调整 */
  header { padding: 0 12px; gap: 10px; }
  .app-brand h1 { font-size: 1.1rem; }
  .brand-text { display: none; } /* 超小屏幕隐藏文字 */
  .quiz-header-wrapper { border-left: none; padding-left: 0; }
  .quiz-info-group { gap: 8px; }
  .quiz-title { max-width: 160px; font-size: 1rem; }
  .score-board { font-size: 0.9em; }
  .divider { display: none; } /* 隐藏分割线 */

  /* 布局调整 */
  .main-content { padding: 16px 12px; }
  .container { width: 100%; }

  /* 侧边栏 - 改为抽屉式 */
  .sidebar {
    position: fixed;
    top: var(--header-height);
    bottom: 0;
    height: auto; /* 让 top 和 bottom 决定高度 */
    z-index: 50; /* 高于 header(20) 和 backdrop(40) */
    box-shadow: 2px 0 12px rgba(0,0,0,0.2);
    transform: translateX(0); /* 默认显示状态由 mobile-open 类控制 */
    display: flex;         /* 确保 Flex 布局生效 */
    flex-direction: column; /* 确保垂直排列 */
  }

  /* 左侧边栏 */
  .left-sidebar {
    left: 0;
    border-right: none;
    transform: translateX(-100%); /* 默认移出屏幕 */
  }
  .left-sidebar.mobile-open {
    transform: translateX(0);
    width: var(--sidebar-width) !important; /* 强制覆盖 collapsed 宽度 */
    opacity: 1 !important;
    pointer-events: auto !important;
  }
  /* collapsed 样式在移动端用于表示隐藏，但我们需要重写它的表现 */
  .left-sidebar.collapsed {
    width: var(--sidebar-width); /* 保持宽度，通过 transform 隐藏 */
  }

  /* 右侧边栏 */
  .right-sidebar {
    right: 0;
    border-left: none;
    transform: translateX(100%);
  }
  .right-sidebar.mobile-open {
    transform: translateX(0);
    width: var(--sidebar-width) !important;
  }
  .right-sidebar.collapsed { width: var(--sidebar-width); }

  /* 隐藏内容逻辑覆盖 */
  .sidebar.collapsed .sidebar-content,
  .sidebar.collapsed .sidebar-header {
    opacity: 1; /* 移动端内容始终保持 opacity 1，通过父级 transform 隐藏 */
    pointer-events: auto;
  }

  /* 侧边栏内容 */
  .sidebar-header { padding: 16px; }
  .new-quiz-btn { font-size: 0.75em; padding: 100px 8px; }
  .sidebar-toggle-btn { display: none; } /* 隐藏原有的侧边切换条 */
  .sidebar-item { height: auto; overflow: visible; } /* 移动端取消固定高度 */
  .sidebar-actions { display: flex; position: static; margin-top: 8px; justify-content: flex-end; background: transparent; box-shadow: none; border: none; gap: 8px; padding: 0; } /* 移动端直接显示操作按钮 */

  /* 题目卡片 */
  .question-card { padding: 20px 16px; margin-bottom: 16px; border-radius: 12px; }
  .q-header { margin-bottom: 16px; }
  .q-content { font-size: 1rem; margin-bottom: 20px; }

  /* 选项与输入 */
  .option-label { padding: 14px 12px; }
  .option-label input { margin-top: 2px; } /* 对齐微调 */
  textarea { height: 140px; }

  /* 底部浮动按钮 */
  .mobile-float-actions {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    z-index: 30;
    display: flex;
    justify-content: center;
  }

  /* 新增：针对底部按钮区域的修复 */
  .sidebar-footer {
    /* 增加底部内边距，避开 iPhone 等设备的底部 Home 横条 */
    padding-bottom: calc(120px + env(safe-area-inset-bottom));
    /* 确保背景色不透明，防止内容重叠 */
    background-color: var(--card-bg);
    /* 确保它在最上层 */
    z-index: 10;
  }

  /* 导入区 */
  .importer-section { padding: 20px; }
  .importer-section h2 { font-size: 1.3rem; }
}

/* 小屏手机适配 (iPhone SE 等) */
@media (max-width: 380px) {
  .quiz-title { max-width: 110px; }
  .app-brand h1 { font-size: 1rem; }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
  animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-content {
  background-color: var(--card-bg);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  color: var(--text);
  animation: slideInFromBottom 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  flex: 1;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 8px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.modal-close:hover {
  background-color: var(--bg);
  color: var(--text);
}

.modal-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: var(--card-bg);
}

.modal-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  justify-content: flex-end;
}

.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quiz-item-checkbox {
  display: flex;
  align-items: flex-start;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background-color: var(--card-bg);
  transition: all 0.2s ease;
  cursor: pointer;
}

.quiz-item-checkbox:hover {
  background-color: var(--bg);
  border-color: var(--primary);
}

.quiz-item-checkbox input {
  margin-top: 4px;
  margin-right: 14px;
  accent-color: var(--primary);
  transform: scale(1.15);
  cursor: pointer;
}

/* 模态框内的表单元素优化 */
.modal-body textarea,
.modal-body input[type="text"],
.modal-body input[type="number"] {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background-color: var(--input-bg);
  color: var(--text);
  font-size: 1rem;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: transparent;
  font-family: inherit;
}

.modal-body textarea:focus,
.modal-body input[type="text"]:focus,
.modal-body input[type="number"]:focus {
  outline: none;
  border-color: var(--primary);
  background-color: var(--card-bg);
  box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
}

.quiz-item-checkbox label {
  flex: 1;
  cursor: pointer;
}

.quiz-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quiz-info .quiz-title {
  font-weight: 500;
  color: var(--text);
}

.quiz-meta {
  font-size: 0.85em;
  color: var(--text-secondary);
  display: flex;
  gap: 12px;
}

.score-info {
  color: var(--primary);
  font-weight: 500;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 85vh;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 16px;
  }

  .quiz-item-checkbox {
    padding: 10px;
  }
}
</style>