<!-- MarkDownReader.vue -->
<template>
  <div ref="viewerContainer" class="ne-doc-major-viewer"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { getApiBaseUrl } from '../../utils/apiConfig';

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

// 处理图片 URL，将相对路径转换为绝对路径
const processImageUrls = (content) => {
  if (!content) return content;
  
  const apiBaseUrl = getApiBaseUrl();
  
  // 匹配各种图片 URL 格式
  // 1. 匹配 <img src="xxx"> 标签中的 src 属性
  // 2. 匹配 markdown 格式的 ![alt](xxx)
  // 3. 匹配 lake 文档格式中的图片 URL
  
  // 处理 HTML img 标签
  let processedContent = content.replace(
    /<img[^>]+src=["']([^"']+)["'][^>]*>/gi,
    (match, src) => {
      if (src.startsWith('http://') || src.startsWith('https://') || src.startsWith('data:')) {
        return match;
      }
      if (src.startsWith('/')) {
        return match.replace(src, `${apiBaseUrl}${src}`);
      }
      return match.replace(src, `${apiBaseUrl}/${src}`);
    }
  );
  
  // 处理 markdown 图片语法 ![alt](url)
  processedContent = processedContent.replace(
    /!\[([^\]]*)\]\(([^)]+)\)/gi,
    (match, alt, url) => {
      if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
        return match;
      }
      if (url.startsWith('/')) {
        return `![${alt}](${apiBaseUrl}${url})`;
      }
      return `![${alt}](${apiBaseUrl}/${url})`;
    }
  );
  
  // 处理 lake 文档格式中的图片 URL（JSON 格式）
  try {
    const lakeDoc = JSON.parse(processedContent);
    if (lakeDoc && lakeDoc.document) {
      const processNode = (node) => {
        if (!node) return node;
        
        if (node.type === 'image' && node.value && node.value.url) {
          const url = node.value.url;
          if (!url.startsWith('http://') && !url.startsWith('https://') && !url.startsWith('data:')) {
            if (url.startsWith('/')) {
              node.value.url = `${apiBaseUrl}${url}`;
            } else {
              node.value.url = `${apiBaseUrl}/${url}`;
            }
          }
        }
        
        if (node.children && Array.isArray(node.children)) {
          node.children = node.children.map(processNode);
        }
        
        return node;
      };
      
      lakeDoc.document = lakeDoc.document.map(processNode);
      processedContent = JSON.stringify(lakeDoc);
    }
  } catch (e) {
    // 如果不是 JSON 格式，忽略错误
  }
  
  return processedContent;
};

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
  return new Promise((resolve, reject) => {
    if (window.Doc && window.React && window.ReactDOM) {
      console.log('脚本已加载，直接使用现有实例');
      resolve();
      return;
    }

    console.log('开始加载脚本...');
    
    // 添加加载超时处理
    const timeoutId = setTimeout(() => {
      console.error('脚本加载超时，使用降级方案');
      resolve(); // 即使超时也继续，使用降级方案
    }, 10000); // 10秒超时

    const reactScript = document.createElement('script');
    reactScript.crossOrigin = 'anonymous';
    reactScript.src = 'https://unpkg.com/react@18/umd/react.production.min.js';
    reactScript.onload = () => {
      console.log('React 加载完成');
      const reactDomScript = document.createElement('script');
      reactDomScript.crossOrigin = 'anonymous';
      reactDomScript.src = 'https://unpkg.com/react-dom@18/umd/react-dom.production.min.js';
      reactDomScript.onload = () => {
        console.log('ReactDOM 加载完成');
        const docScript = document.createElement('script');
        docScript.src = 'https://gw.alipayobjects.com/render/p/yuyan_npm/@alipay_lakex-doc/1.24.0/umd/doc.umd.js';
        docScript.onload = () => {
          console.log('Doc 脚本加载完成');
          clearTimeout(timeoutId);
          resolve();
        };
        docScript.onerror = () => {
          console.error('Doc 脚本加载失败，使用降级方案');
          clearTimeout(timeoutId);
          resolve(); // 即使加载失败也继续，使用降级方案
        };
        document.body.appendChild(docScript);
      };
      reactDomScript.onerror = () => {
        console.error('ReactDOM 加载失败');
        clearTimeout(timeoutId);
        reject(new Error('ReactDOM 加载失败'));
      };
      document.body.appendChild(reactDomScript);
    };
    reactScript.onerror = () => {
      console.error('React 加载失败');
      clearTimeout(timeoutId);
      reject(new Error('React 加载失败'));
    };
    document.body.appendChild(reactScript);
  });
};

// 初始化阅读器并设置内容
const initViewer = (content) => {
  console.log('开始初始化阅读器，内容长度:', content ? content.length : 0);
  
  // 处理内容中的图片 URL
  const processedContent = processImageUrls(content || '<p>无正文内容</p>');
  console.log('处理后的内容长度:', processedContent.length);
  
  if (viewerContainer.value && window.Doc) {
    console.log('使用 Doc 实例渲染内容');

    // 销毁旧实例（避免重复创建）
    if (viewer && viewer.destroy) {
      console.log('销毁旧的阅读器实例');
      viewer.destroy();
    }
    // 创建新实例
    try {
      viewer = window.Doc.createOpenViewer(viewerContainer.value, {
        darkMode: true
      });
      // 设置内容
      viewer.setDocument('text/lake', processedContent);
      console.log('阅读器初始化成功');
    } catch (error) {
      console.error('阅读器初始化失败:', error);
      // 使用降级方案
      useFallbackRender(processedContent);
    }
  } else {
    console.log('Doc 实例不可用，使用降级方案');
    // 使用降级方案
    useFallbackRender(processedContent);
  }
};

// 降级渲染方案（当 Doc 不可用时）
const useFallbackRender = (content) => {
  if (viewerContainer.value) {
    console.log('使用降级方案渲染内容');
    // 清空容器
    viewerContainer.value.innerHTML = '';
    
    // 创建一个简单的 div 来显示内容
    const contentDiv = document.createElement('div');
    contentDiv.className = 'fallback-content';
    contentDiv.style.padding = '20px';
    contentDiv.style.color = '#e0e0e0';
    contentDiv.style.lineHeight = '1.6';
    
    // 尝试解析内容
    try {
      // 检查是否为 JSON 格式
      const parsedContent = JSON.parse(content);
      if (parsedContent && parsedContent.document) {
        // 渲染 Lake 文档格式
        contentDiv.innerHTML = renderLakeContent(parsedContent.document);
      } else {
        // 直接显示内容
        contentDiv.textContent = '无法解析内容';
      }
    } catch (e) {
      // 不是 JSON 格式，尝试直接显示
      try {
        // 尝试作为 HTML 渲染
        contentDiv.innerHTML = content;
      } catch (err) {
        // 作为纯文本渲染
        contentDiv.textContent = content;
      }
    }
    
    viewerContainer.value.appendChild(contentDiv);
  }
};

// 渲染 Lake 文档内容
const renderLakeContent = (documentNodes) => {
  if (!Array.isArray(documentNodes)) return '';
  
  let html = '';
  
  documentNodes.forEach(node => {
    if (node.type === 'paragraph') {
      html += `<p>${renderNodeChildren(node.children)}</p>`;
    } else if (node.type === 'heading1') {
      html += `<h1>${renderNodeChildren(node.children)}</h1>`;
    } else if (node.type === 'heading2') {
      html += `<h2>${renderNodeChildren(node.children)}</h2>`;
    } else if (node.type === 'heading3') {
      html += `<h3>${renderNodeChildren(node.children)}</h3>`;
    } else if (node.type === 'image') {
      if (node.value && node.value.url) {
        console.log('渲染图片:', node.value.url);
        html += `<img src="${node.value.url}" alt="${node.value.alt || ''}" style="max-width: 100%; height: auto; margin: 10px 0;" />`;
      }
    } else if (node.type === 'text') {
      html += node.value || '';
    }
  });
  
  return html;
};

// 渲染节点子元素
const renderNodeChildren = (children) => {
  if (!Array.isArray(children)) return '';
  
  let html = '';
  children.forEach(child => {
    if (child.type === 'text') {
      html += child.value || '';
    } else if (child.type === 'image') {
      if (child.value && child.value.url) {
        console.log('渲染子元素图片:', child.value.url);
        html += `<img src="${child.value.url}" alt="${child.value.alt || ''}" style="max-width: 100%; height: auto; margin: 10px 0;" />`;
      }
    }
  });
  
  return html;
};

// 监听content变化，动态更新内容
watch(
    () => props.content,
    (newContent) => {
      console.log('内容变化，重新渲染');
      if (viewer) {
        const processedContent = processImageUrls(newContent || '<p>无正文内容</p>');
        viewer.setDocument('text/lake', processedContent);
      } else {
        initViewer(newContent);
      }
    },
    { immediate: true } // 初始加载时立即执行
);

onMounted(async () => {
  console.log('组件挂载，开始初始化');
  removeStyles = loadStyles();
  try {
    await loadScripts(); // 确保脚本加载完成
    initViewer(props.content);
  } catch (error) {
    console.error('初始化失败:', error);
    // 即使出错也使用降级方案
    initViewer(props.content);
  }
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