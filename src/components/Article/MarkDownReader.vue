<!-- MarkDownReader.vue -->
<template>
  <div ref="viewerContainer" class="ne-doc-major-viewer"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

// 接收父组件传递的正文内容（必传，默认空字符串）
// eslint-disable-next-line no-undef
const props = defineProps({
  content: {
    type: String,
    default: ''
  }
});

const viewerContainer = ref(null);
let viewer = null;
let removeStyles = null;

// 动态加载样式
const loadStyles = () => {
  const docStyle = document.createElement('link');
  docStyle.rel = 'stylesheet';
  docStyle.href = 'https://gw.alipayobjects.com/render/p/yuyan_npm/@alipay_lakex-doc/1.24.0/umd/doc.css';
  document.head.appendChild(docStyle);

  const antdStyle = document.createElement('link');
  antdStyle.rel = 'stylesheet';
  antdStyle.href = 'https://unpkg.com/antd@4.24.13/dist/antd.css';
  document.head.appendChild(antdStyle);

  return () => {
    document.head.removeChild(docStyle);
    document.head.removeChild(antdStyle);
  };
};

// 动态加载脚本
const loadScripts = () => {
  return new Promise((resolve) => {
    if (window.Doc && window.React && window.ReactDOM) {
      resolve();
      return;
    }

    const reactScript = document.createElement('script');
    reactScript.crossOrigin = 'anonymous';
    reactScript.src = 'https://unpkg.com/react@18/umd/react.production.min.js';
    reactScript.onload = () => {
      const reactDomScript = document.createElement('script');
      reactDomScript.crossOrigin = 'anonymous';
      reactDomScript.src = 'https://unpkg.com/react-dom@18/umd/react-dom.production.min.js';
      reactDomScript.onload = () => {
        const docScript = document.createElement('script');
        docScript.src = 'https://gw.alipayobjects.com/render/p/yuyan_npm/@alipay_lakex-doc/1.24.0/umd/doc.umd.js';
        docScript.onload = () => resolve();
        document.body.appendChild(docScript);
      };
      document.body.appendChild(reactDomScript);
    };
    document.body.appendChild(reactScript);
  });
};

// 初始化阅读器并设置内容
const initViewer = (content) => {
  if (viewerContainer.value && window.Doc) {

    // 销毁旧实例（避免重复创建）
    if (viewer && viewer.destroy) viewer.destroy();
    // 创建新实例
    viewer = window.Doc.createOpenViewer(viewerContainer.value, {
      darkMode: true
    });
    // 设置内容（使用父组件传递的content）
    viewer.setDocument('text/lake', content || '<p>无正文内容</p>');
  }
};

// 监听content变化，动态更新内容
watch(
    () => props.content,
    (newContent) => {
      if (viewer) {
        viewer.setDocument('text/lake', newContent || '<p>无正文内容</p>');
      }
    },
    { immediate: true } // 初始加载时立即执行
);

onMounted(async () => {
  removeStyles = loadStyles();
  await loadScripts(); // 确保脚本加载完成
  initViewer(props.content);
});

onUnmounted(() => {
  if (removeStyles) removeStyles();
  if (viewer && viewer.destroy) viewer.destroy();
});
</script>

<style scoped>
.ne-doc-major-viewer {
  width: 100%;
  min-height: 300px;
  text-align: left;
}
</style>