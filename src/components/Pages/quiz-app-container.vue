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
          <button
              class="btn secondary sm new-quiz-btn"
              @click="createNewQuiz"
          >
            新试卷
          </button>
        </div>
        <div class="sidebar-content">
          <ul class="sidebar-list">
            <li v-if="reversedHistory.length === 0" class="empty-list-item">暂无记录</li>
            <li
                v-for="quiz in reversedHistory"
                :key="quiz.id"
                class="sidebar-item"
                :class="{ active: currentQuizId === quiz.id && !isViewingWrongOnly }"
                @click="loadQuiz(quiz.id, false)"
            >
              <span v-if="quiz.isSubmitted" class="score-tag" :class="getScoreClass(quiz)">
                {{ getQuizScore(quiz) }}/{{ quiz.questions.length }}
              </span>
              <div class="quiz-item-title">{{ quiz.title }}</div>
              <span class="date">{{ formatDate(quiz.timestamp) }}</span>
              <div class="sidebar-actions">
                <button class="action-btn" @click.stop="renameQuiz(quiz.id)">✏️</button>
                <button class="action-btn delete" @click.stop="deleteQuiz(quiz.id)">🗑️</button>
              </div>
            </li>
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
                v-for="(q, index) in questionsToShow"
                :key="q.id"
                class="question-card"
                :class="{
                  'status-correct': currentQuiz.isSubmitted && checkAnswer(q),
                  'status-wrong': currentQuiz.isSubmitted && !checkAnswer(q)
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
                <label v-for="opt in q.options" :key="opt.label" class="option-label">
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
                <label v-for="opt in q.options" :key="opt.label" class="option-label">
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

// 自动滚题相关状态
const isAutoScroll = ref(true); // 自动滚题开关，默认开启
const showNextButton = ref(false); // 下一题按钮显示状态
const currentQuestionIndex = ref(0); // 当前题目索引
const showMultiChoiceHint = ref(false); // 多选题提示显示状态

// Export Modal State
const showExportModalFlag = ref(false);
const selectedQuizzes = ref([]);

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

// === 生命周期与持久化 ===
onMounted(async () => {
  // 检查登录状态
  await userStore.initUser();
  if (!userStore.isLogin) {
    router.push('/');
    return;
  }
  
  loadHistory();
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
  
  // 更新当前题目索引
  currentQuestionIndex.value = index;
  
  // 多选题提示
  if (q.type === 'multiple' && isAutoScroll.value && !showMultiChoiceHint.value) {
    showMultiChoiceHint.value = true;
    // 3秒后自动隐藏提示
    setTimeout(() => {
      showMultiChoiceHint.value = false;
    }, 3000);
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

// 跳转到下一题
function goToNextQuestion() {
  if (!currentQuiz.value) return;
  
  const totalQuestions = questionsToShow.value.length;
  const nextIndex = currentQuestionIndex.value + 1;
  
  if (nextIndex < totalQuestions) {
    // 有下一题，滚动到下一题
    currentQuestionIndex.value = nextIndex;
    scrollToQuestion(nextIndex);
    showNextButton.value = false; // 滚动后隐藏下一题按钮
  } else {
    // 没有下一题，检查是否需要提交
    if (!currentQuiz.value.isSubmitted) {
      // 自动提交
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
  });
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
  --primary: #4a7c59;
  --primary-hover: #3a6345;
  --success: #609966;
  --danger: #cf5c5c;
  --warning: #d4a373;
  --bg: #f7f7f4;
  --card-bg: #ffffff;
  --text: #2d3436;
  --text-secondary: #636e72;
  --text-light: #b2bec3;
  --border: #e6e6e2;
  --border-light: #f0f0ed;
  --input-bg: #fafaf9;
  --shadow: 0 4px 20px -2px rgba(45, 52, 54, 0.08);
  --shadow-lg: 0 10px 15px -3px rgba(45, 52, 54, 0.1);
  --sidebar-width: 280px;
  --header-height: 64px;


  /* --- 🆕 新增：滚动条专用变量 (浅色模式) --- */
  /* 轨道背景设为透明，看起来更现代 */
  --scrollbar-track: transparent;
  /* 滑块颜色：使用浅灰色，不抢眼 */
  --scrollbar-thumb: #c8c8c6;
  /* 悬停颜色：加深灰色 */
  --scrollbar-thumb-hover: #a0a09e;
  /* 滚动条宽度 */
  --scrollbar-width: 10px;

}
/* Dark Mode 适配 */
[data-theme="dark"] {
  --primary: #8ebf95;
  --primary-hover: #4a7c59;
  --success: #609966;
  --danger: #cf5c5c;
  --warning: #d4a373;
  --bg: #1c1c1c;
  --card-bg: #262626;
  --text: #e0e0e0;
  --text-secondary: #a3a3a3;
  --text-light: #b2bec3;
  --border: #333333;
  --border-light: #404040;
  --input-bg: #2d2d2d;
  --shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3);

  /* --- 🆕 新增：滚动条专用变量 (深色模式) --- */
  /* 深色模式下，滑块需要比背景略亮 */
  --scrollbar-track: transparent;
  --scrollbar-thumb: #404040;
  --scrollbar-thumb-hover: #505050;
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
  font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  line-height: 1.5;
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
  box-shadow: var(--shadow);
  z-index: 60;
  gap: 20px;
  flex-shrink: 0;
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
  font-weight: 600;
  font-size: 1.1em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
  max-width: 300px;
}

.quiz-action-group {
  display: flex;
  align-items: center;
  gap: 16px;
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
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
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
  transition: .3s;
  border-radius: 24px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: var(--success);
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

input:focus + .toggle-slider {
  box-shadow: 0 0 1px var(--success);
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
  width: var(--sidebar-width);
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
  width: 0;
  border: none;
}

.sidebar.collapsed .sidebar-content,
.sidebar.collapsed .sidebar-header {
  opacity: 0;
  pointer-events: none;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  white-space: nowrap;
  color: var(--text);
  background-color: var(--card-bg);
  flex-shrink: 0;
}
.new-quiz-btn {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
  color: white;
  transform-origin: right center;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  min-height: 0;
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
}

.sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-item {
  padding: 16px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid var(--border-light);
  font-size: 0.9em;
  position: relative;
  transition: all 0.3s ease;
  background-color: var(--card-bg);
  color: var(--text);
}

.sidebar-item:hover {
  background-color: var(--bg);
  border-color: var(--primary);
  box-shadow: var(--shadow);
}

.sidebar-item.active {
  background-color: var(--bg);
  border-color: var(--primary);
  color: var(--primary);
}

.sidebar-item .date {
  font-size: 0.8em;
  color: var(--text-secondary);
  display: block;
  margin-top: 6px;
}

.wrong-count {
  color: var(--danger) !important;
  font-weight: 600;
}

.quiz-item-title {
  font-weight: 500;
  color: var(--text);
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.score-tag {
  float: right;
  font-weight: 600;
  font-size: 0.85em;
  padding: 2px 8px;
  border-radius: 12px;
  background-color: var(--bg);
}
.score-tag.good { color: var(--success); border: 1px solid var(--success); }
.score-tag.bad { color: var(--danger); border: 1px solid var(--danger); }

.sidebar-actions {
  position: absolute;
  right: 8px;
  top: 8px;
  display: none;
  gap: 4px;
  background-color: var(--card-bg);
  padding: 2px;
  border-radius: 6px;
  box-shadow: var(--shadow);
}
.sidebar-item:hover .sidebar-actions { display: flex; }

.action-btn {
  background: var(--bg);
  border: 1px solid var(--border);
  cursor: pointer;
  font-size: 0.9em;
  padding: 4px 6px;
  border-radius: 4px;
  color: var(--text-secondary);
}
.action-btn:hover { background-color: var(--primary); color: white; border-color: var(--primary); }
.action-btn.delete:hover { background-color: var(--danger); border-color: var(--danger); }

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
  padding: 28px;
  border-radius: 16px;
  box-shadow: var(--shadow);
  margin-bottom: 24px;
  border: 1px solid var(--border);
  border-left: 6px solid transparent;
  width: 100%;
  max-width: 850px;
  box-sizing: border-box;
  text-align: left;
}

.question-card.status-correct { border-left-color: var(--success); background-color: rgba(16, 185, 129, 0.05); }
.question-card.status-wrong { border-left-color: var(--danger); background-color: rgba(239, 68, 68, 0.05); }

.q-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; gap: 12px; }

.remove-btn {
  font-size: 0.85em;
  padding: 6px 12px;
  white-space: nowrap;
}
.q-index { font-weight: 600; font-size: 1.1em; color: var(--text); flex: 1; }

.q-content { font-size: 1.1em; margin-bottom: 24px; line-height: 1.7; color: var(--text); }
:deep(.q-content img) { max-width: 100%; height: auto; border-radius: 8px; }
:deep(.q-content table) { width: 100%; overflow-x: auto; display: block; border-collapse: collapse; }
:deep(.q-content table th), :deep(.q-content table td) { border: 1px solid var(--border); padding: 8px; }

.options-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 20px; }

.option-label {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  cursor: pointer;
  background-color: var(--card-bg);
  color: var(--text);
  /* 防止手机点击高亮背景太丑 */
  -webkit-tap-highlight-color: transparent;
}

.option-label:hover { background-color: var(--bg); border-color: var(--primary); }
.option-label input { margin-top: 4px; margin-right: 12px; accent-color: var(--primary); transform: scale(1.2); }
.option-text { line-height: 1.5; color: var(--text); word-break: break-word; }
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
  background-color: var(--primary); color: white; border: none; padding: 10px 20px;
  border-radius: 10px; cursor: pointer; font-size: 0.95em; font-weight: 600;
  transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
}
.btn.secondary { background-color: var(--text-secondary); }
.btn.sm { padding: 6px 12px; font-size: 0.85em; }
.btn.full-width { width: 100%; padding: 14px; font-size: 1.1em; }
.shadow-btn { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }

/* 移动端遮罩 */
.mobile-backdrop {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); z-index: 40;
  backdrop-filter: blur(2px);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

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
  .sidebar-actions { display: flex; position: static; margin-top: 8px; justify-content: flex-end; background: transparent; box-shadow: none; } /* 移动端直接显示操作按钮 */

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
  backdrop-filter: blur(2px);
}

.modal-content {
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  color: var(--text);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.modal-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.quiz-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quiz-item-checkbox {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background-color: var(--card-bg);
}

.quiz-item-checkbox input {
  margin-top: 4px;
  margin-right: 12px;
  accent-color: var(--primary);
  transform: scale(1.2);
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