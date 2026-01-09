<template>
  <div class="quiz-app-container">
    <header>
      <div class="app-brand">
        <h1>📋 试题解析工具 Pro</h1>
      </div>

      <div v-if="currentQuizId" class="quiz-header-wrapper">
        <div class="quiz-info-group">
          <span class="quiz-title" :title="currentQuiz.title">{{ currentQuiz.title }}</span>
          <span v-if="isViewingWrongOnly" class="tag mode-badge">错题模式</span>
        </div>

        <div class="quiz-action-group">
          <div v-if="currentQuiz.isSubmitted && !isViewingWrongOnly" class="score-board">
            得分: <span class="score-highlight">{{ currentScore }}</span> / <span>{{ currentTotal }}</span>
          </div>

          <div v-if="currentQuiz.isSubmitted && !isViewingWrongOnly" class="divider"></div>

          <template v-if="!isViewingWrongOnly">
            <button v-if="!currentQuiz.isSubmitted" class="btn" @click="submitQuiz">提交判卷</button>
            <button v-else class="btn secondary" @click="resetCurrentQuiz">重做本卷</button>
          </template>
        </div>
      </div>

      <button class="theme-toggle" @click="toggleTheme" title="切换深色/浅色模式">
        {{ isDark ? '☀️' : '🌙' }}
      </button>
    </header>

    <div class="app-layout">
      <aside class="sidebar" :class="{ collapsed: leftSidebarCollapsed }">
        <div class="sidebar-header">
          <span>📚 历史试卷</span>
          <button class="btn secondary sm" @click="createNewQuiz">新试卷</button>
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
                <button class="action-btn" @click.stop="renameQuiz(quiz.id)" title="重命名">✏️</button>
                <button class="action-btn delete" @click.stop="deleteQuiz(quiz.id)" title="删除">🗑️</button>
              </div>
            </li>
          </ul>
        </div>
        <div class="sidebar-toggle-btn left-toggle" @click="leftSidebarCollapsed = !leftSidebarCollapsed">
          {{ leftSidebarCollapsed ? '▶' : '◀' }}
        </div>
      </aside>

      <main class="main-content">
        <div class="container">
          <div v-if="!currentQuizId && quizHistory.length === 0" class="importer-section">
            <h2>新建试卷</h2>
            <p class="importer-desc">粘贴 HTML 源码（支持普通网页和 Angular/MOOC 格式）：</p>
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

          <div v-else-if="!currentQuizId && quizHistory.length > 0" class="empty-state">
            <h3>👈 请从左侧选择试卷或点击“新试卷”导入</h3>
          </div>

          <div v-if="currentQuizId && currentQuiz" class="quiz-area">
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
            >
              <div class="q-header">
                <span>{{ q.meta || `题目 ${index + 1}` }}</span>
                <span class="tag type">{{ getTypeLabel(q.type) }}</span>
              </div>

              <div class="q-content" v-html="q.content"></div>

              <div v-if="q.type === 'single'" class="options-list">
                <label v-for="opt in q.options" :key="opt.label" class="option-label">
                  <input
                      type="radio"
                      :name="`q-${q.id}`"
                      :value="opt.label"
                      v-model="q.userAnswer"
                      :disabled="currentQuiz.isSubmitted || isViewingWrongOnly"
                      @change="saveHistory"
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
                      :disabled="currentQuiz.isSubmitted || isViewingWrongOnly"
                      @change="(e) => toggleCheckbox(q, opt.label, e.target.checked)"
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
                    :disabled="currentQuiz.isSubmitted || isViewingWrongOnly"
                    @input="saveHistory"
                >
              </div>

              <div v-if="currentQuiz.isSubmitted" class="result-analysis">
                <p>
                  <span class="tag correct-ans">正确答案</span>
                  <strong>{{ q.correctAnswer }}</strong>
                </p>
                <p>
                  <span class="tag" :class="checkAnswer(q) ? 'correct-ans' : 'wrong-ans'">你的答案</span>
                  <span>{{ q.userAnswer || '(未作答)' }}</span>
                </p>
                <div v-if="q.explanation" class="explanation-box">
                  <strong>💡 试题解析</strong>
                  {{ q.explanation }}
                </div>
              </div>

            </div>
          </div>
        </div>
      </main>

      <aside class="sidebar" :class="{ collapsed: rightSidebarCollapsed }">
        <div class="sidebar-header">
          <span>❌ 错题本</span>
          <small style="color: var(--text-secondary)">只看错题</small>
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
              <div>{{ item.title }}</div>
              <span class="date">错题数: <span style="color:var(--danger)">{{ item.wrongCount }}</span></span>
            </li>
          </ul>
        </div>
        <div class="sidebar-toggle-btn right-toggle" @click="rightSidebarCollapsed = !rightSidebarCollapsed">
          {{ rightSidebarCollapsed ? '◀' : '▶' }}
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, } from 'vue';

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

// === 计算属性 ===
const reversedHistory = computed(() => {
  return [...quizHistory.value].reverse();
});

const wrongHistoryItems = computed(() => {
  return reversedHistory.value
      .filter(quiz => quiz.isSubmitted)
      .map(quiz => {
        const wrongCount = quiz.questions.filter(q => !checkAnswer(q)).length;
        return { ...quiz, wrongCount };
      })
      .filter(item => item.wrongCount > 0);
});

const currentQuiz = computed(() => {
  return quizHistory.value.find(q => q.id === currentQuizId.value) || null;
});

const questionsToShow = computed(() => {
  if (!currentQuiz.value) return [];
  if (isViewingWrongOnly.value && currentQuiz.value.isSubmitted) {
    return currentQuiz.value.questions.filter(q => !checkAnswer(q));
  }
  return currentQuiz.value.questions;
});

const currentScore = computed(() => {
  if (!currentQuiz.value) return 0;
  return currentQuiz.value.questions.filter(q => checkAnswer(q)).length;
});

const currentTotal = computed(() => {
  return currentQuiz.value ? currentQuiz.value.questions.length : 0;
});

// === 生命周期与持久化 ===
onMounted(() => {
  loadHistory();
  applyThemeFromStorage();
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

function saveHistory() {
  // 触发 watch
  // 实际上由于 quizHistory 是 ref 且 deep watch，修改 userAnswer 会自动触发保存
  // 这里手动保留函数是为了兼容性或显式调用
}

// === 业务逻辑 ===

function createNewQuiz() {
  currentQuizId.value = null;
  htmlInput.value = '';
  parseError.value = '';
}

function loadQuiz(id, wrongOnly) {
  currentQuizId.value = id;
  isViewingWrongOnly.value = wrongOnly;
  window.scrollTo({ top: 0, behavior: 'smooth' });
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
  }
}

function submitQuiz() {
  if (currentQuiz.value) {
    currentQuiz.value.isSubmitted = true;
    isViewingWrongOnly.value = false; // 提交后显示全卷结果
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function resetCurrentQuiz() {
  if (!confirm("确定要清空当前答案重新开始吗？")) return;
  if (currentQuiz.value) {
    currentQuiz.value.isSubmitted = false;
    currentQuiz.value.questions.forEach(q => q.userAnswer = '');
    isViewingWrongOnly.value = false;
  }
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

function formatDate(ts) {
  return new Date(ts).toLocaleString();
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
  if (type === 'single') return '单选题/判断';
  if (type === 'multiple') return '多选题';
  return '简答/填空';
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

function showDemoHelp() {
  alert("请复制题目网页的 HTML 源码粘贴到输入框中。");
}

// === 主题切换 (带 View Transitions) ===
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

// === 解析核心逻辑 ===
function parseAndGenerate() {
  const input = htmlInput.value;
  if (!input.trim()) return;

  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(input, 'text/html');
    let questions = [];

    // 尝试查找常规题目结构
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
    parseError.value = '';

  } catch (e) {
    console.error(e);
    parseError.value = "解析错误: " + e.message;
  }
}

function fixHtmlContent(html) {
  if (!html) return '';
  return html.replace(/src="\/\//g, 'src="https://');
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

    // 补丁：如果没找到正确答案，尝试从用户正确结果推断
    if (!q.correctAnswer) {
      // 这里需要注意，原逻辑是根据 .result-correct，但新试卷还没做
      // 如果是已做过的试卷导入，可以尝试提取
      // 这里简化处理
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

<style scoped>
:root {
  /* 亮色模式变量 */
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --success: #10b981;
  --danger: #ef4444;
  --bg: #f3f4f6;
  --card-bg: #ffffff;
  --text: #1f2937;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
  --input-bg: #ffffff;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --sidebar-width: 260px;
  --header-height: 64px;
}

/* Vue scoped CSS 不直接支持 :root 变量定义在组件内影响全局。
  但为了单文件组件的完整性，这里使用 ::v-deep 或直接写在组件根class上，
  或者依赖外部CSS。鉴于这是迁移，我们直接使用数据属性选择器来模拟。
*/

.quiz-app-container {
  --primary: #3b82f6;
  --primary-hover: #2563eb;
  --success: #10b981;
  --danger: #ef4444;
  --bg: #f3f4f6;
  --card-bg: #ffffff;
  --text: #1f2937;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
  --input-bg: #ffffff;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --sidebar-width: 260px;
  --header-height: 64px;
  --scrollbar-track: #f3f4f6;
  --scrollbar-thumb: #d1d5db;
  --scrollbar-thumb-hover: #9ca3af;

  font-family: 'Segoe UI', system-ui, sans-serif;
  background-color: var(--bg);
  color: var(--text);
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 全局 Dark Mode 处理 - Vue 中通过 documentElement 属性匹配 */
:global([data-theme="dark"]) .quiz-app-container {
  --primary: #60a5fa;
  --primary-hover: #3b82f6;
  --success: #34d399;
  --danger: #f87171;
  --bg: #111827;
  --card-bg: #1f2937;
  --text: #f3f4f6;
  --text-secondary: #9ca3af;
  --border: #374151;
  --input-bg: #374151;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
  --scrollbar-track: #111827;
  --scrollbar-thumb: #4b5563;
  --scrollbar-thumb-hover: #6b7280;
}

/* 滚动条 */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--scrollbar-track); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-thumb-hover); }

/* 头部 */
header {
  height: var(--header-height);
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  padding: 0 20px;
  box-shadow: var(--shadow);
  z-index: 20;
  gap: 20px;
  view-transition-name: header;
}

.app-brand h1 {
  font-size: 1.2rem;
  margin: 0;
  white-space: nowrap;
}

.quiz-header-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-left: 1px solid var(--border);
  padding-left: 20px;
  height: 40px;
}

.quiz-info-group {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow: hidden;
}

.quiz-title {
  font-weight: bold;
  font-size: 1.1em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.quiz-action-group {
  display: flex;
  align-items: center;
  gap: 15px;
}

.score-board {
  font-weight: bold;
  color: var(--text);
  font-size: 1.05em;
  white-space: nowrap;
}

.score-highlight {
  color: var(--primary);
}

.divider {
  border-left: 1px solid var(--border);
  height: 24px;
}

.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 1.2rem;
  margin-left: auto;
  outline: none;
}
.theme-toggle:hover { background-color: var(--bg); }

/* 布局 */
.app-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  position: relative;
}

.sidebar {
  width: var(--sidebar-width);
  background-color: var(--card-bg);
  border-right: 1px solid var(--border);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  position: relative;
  z-index: 10;
}
.sidebar.collapsed { width: 0; border: none; }
.sidebar.collapsed .sidebar-content, .sidebar.collapsed .sidebar-header { opacity: 0; pointer-events: none; }

.sidebar-header {
  padding: 15px;
  font-weight: bold;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  white-space: nowrap;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-item {
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  font-size: 0.9em;
  position: relative;
}
.sidebar-item:hover { background-color: var(--bg); }
.sidebar-item.active { background-color: var(--bg); border-color: var(--primary); color: var(--primary); }
.sidebar-item .date { font-size: 0.8em; color: var(--text-secondary); display: block; margin-top: 4px; }

.score-tag { float: right; font-weight: bold; font-size: 0.9em; }
.score-tag.good { color: var(--success); }
.score-tag.bad { color: var(--danger); }

.sidebar-actions {
  position: absolute;
  right: 5px;
  top: 5px;
  display: none;
  gap: 4px;
  background-color: var(--card-bg);
  padding-left: 5px;
  border-radius: 4px;
}
.sidebar-item:hover .sidebar-actions { display: flex; }

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1em;
  padding: 2px 4px;
  border-radius: 3px;
  color: var(--text-secondary);
}
.action-btn:hover { background-color: var(--bg); color: var(--text); }
.action-btn.delete:hover { color: var(--danger); }

.sidebar-toggle-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 40px;
  background-color: var(--card-bg);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 20;
  font-size: 12px;
}
.sidebar-toggle-btn:hover { background-color: var(--primary); color: white; border-color: var(--primary); }
.left-toggle { right: -20px; border-top-right-radius: 8px; border-bottom-right-radius: 8px; border-left: none; }
.right-toggle { left: -20px; border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-right: none; }

/* 主内容 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: var(--bg);
}
.container { max-width: 800px; margin: 0 auto; }

/* 导入区 */
.importer-section {
  background: var(--card-bg);
  padding: 25px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
}
.importer-desc { color: var(--text-secondary); font-size: 0.9em; }

textarea {
  width: 100%;
  height: 150px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-family: monospace;
  box-sizing: border-box;
  margin-bottom: 15px;
  resize: vertical;
  background-color: var(--input-bg);
  color: var(--text);
}

.btn-group { display: flex; gap: 10px; }
.parse-error { color: var(--danger); margin-top: 10px; }

/* 按钮 */
.btn {
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}
.btn:hover { background-color: var(--primary-hover); }
.btn.secondary { background-color: var(--text-secondary); }
.btn.sm { padding: 2px 8px; font-size: 12px; }

/* 题目卡片 */
.question-card {
  background: var(--card-bg);
  padding: 25px;
  border-radius: 12px;
  box-shadow: var(--shadow);
  margin-bottom: 20px;
  border: 1px solid var(--border);
  border-left: 5px solid transparent;
  transition: all 0.3s ease;
}
.question-card.status-correct { border-left-color: var(--success); background-color: rgba(16, 185, 129, 0.05); }
.question-card.status-wrong { border-left-color: var(--danger); background-color: rgba(239, 68, 68, 0.05); }

.q-header { display: flex; justify-content: space-between; margin-bottom: 15px; font-weight: bold; color: var(--text-secondary); font-size: 0.9em; }
.q-content { font-size: 1.1em; margin-bottom: 20px; }
:deep(.q-content img) { max-width: 100%; height: auto; border-radius: 4px; }

.options-list { display: flex; flex-direction: column; gap: 10px; }
.option-label {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
}
.option-label:hover { background-color: var(--bg); }
.option-label input { margin-top: 5px; margin-right: 12px; }

.short-answer-input {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1rem;
  box-sizing: border-box;
  background-color: var(--input-bg);
  color: var(--text);
}

.result-analysis {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px dashed var(--border);
}
.explanation-box {
  margin-top: 15px;
  padding: 12px;
  background-color: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 0.95em;
  line-height: 1.6;
}
.explanation-box strong { color: var(--text); display: block; margin-bottom: 5px; }

.tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-right: 5px; }
.tag.correct-ans { background: rgba(16, 185, 129, 0.2); color: var(--success); }
.tag.wrong-ans { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
.tag.type { background: var(--primary); color: white; opacity: 0.8; }
.tag.mode-badge { background: var(--danger); color: white; }

.empty-state { text-align: center; padding: 50px 20px; color: var(--text-secondary); }
.empty-list-item { padding: 10px; color: var(--text-secondary); text-align: center; }

/* noinspection CssInvalidPseudoSelector */
::view-transition-old(root),
  /* noinspection CssInvalidPseudoSelector */
::view-transition-new(root) {
  animation: none;
  mix-blend-mode: normal;
}
</style>