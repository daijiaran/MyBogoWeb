<template>
  <div class="editor-wrapper">
    <div id="root" class="ne-doc-major-editor"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, nextTick, ref, watch } from 'vue'
import { getApiBaseUrl } from '../../utils/apiConfig';

// eslint-disable-next-line no-undef
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  isMobile: { // 新增：接收父组件传递的移动端标识
    type: Boolean,
    default: false
  }
})

// eslint-disable-next-line no-undef
const emit = defineEmits(['update:modelValue', 'save-request'])
const editor = ref(null)

// 图片上传函数 - 支持进度回调
const uploadImage = async (file, {onSuccess, onError}) => {
  if (!file) {
    onError(new Error('未选择文件'))
    return
  }

  if (file.size <= 0) {
    console.error('【uploadImage】错误：文件大小为0（无效文件）')
    onError(new Error('图片文件内容为空'))
    return
  }

  // 前端文件类型验证
  const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!validTypes.includes(file.type)) {
    onError(new Error('仅支持 JPEG、PNG、GIF、WebP 格式的图片'))
    return
  }

  // 前端文件大小验证（10MB）
  if (file.size > 10 * 1024 * 1024) {
    onError(new Error('文件大小不能超过10MB'))
    return
  }

  const formData = new FormData()
  formData.append('timestamp', Date.now())
  formData.append('image', file, file.name || `image-${Date.now()}.${file.type.split('/')[1]}`)

  // 验证FormData
  let hasValidImage = false
  formData.forEach((value, key) => {
    if (key === 'image' && (value instanceof File || value instanceof Blob) && value.size > 0) {
      hasValidImage = true
    }
  })
  if (!hasValidImage) {
    console.error('【uploadImage】严重错误：FormData中未添加有效的image参数')
    onError(new Error('文件上传参数异常'))
    return
  }

  try {
    const abortController = new AbortController()
    const timeoutId = setTimeout(() => abortController.abort(), 30000)

    const token = localStorage.getItem('token')
    const apiBaseUrl = getApiBaseUrl()
    const response = await fetch(`${apiBaseUrl}/api/upload/image`, {
      method: 'POST',
      body: formData,
      signal: abortController.signal,
      headers: {
        ...(token ? {'Authorization': `Bearer ${token}`} : {})
      },
      credentials: 'include'
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      console.error(`【uploadImage】HTTP错误: ${response.status}`, errorText)
      onError(new Error(`上传失败 (HTTP ${response.status})`))
      return
    }

    const result = await response.json()
    console.log('【uploadImage】响应数据:', result)

    if (result.code === 200 && result.data) {
      onSuccess(result.data)
    } else {
      onError(new Error(result.message || '上传失败'))
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('【uploadImage】请求超时')
      onError(new Error('上传超时，请稍后重试'))
    } else if (error.name === 'TypeError') {
      console.error('【uploadImage】网络错误或请求被阻止')
      onError(new Error('网络连接失败，请检查网络设置'))
    } else {
      console.error('【uploadImage】上传失败:', error)
      onError(new Error(error.message || '图片上传失败'))
    }
  }
}

// 监听窗口大小变化，实现自适应
const handleResize = () => {
  if (editor.value) {
    // 触发编辑器重新计算布局
    setTimeout(() => {
      const editorInstance = editor.value
      if (editorInstance && typeof editorInstance.refresh === 'function') {
        editorInstance.refresh()
      }
    }, 100)
  }
}

// 初始化编辑器
const initEditor = () => {
  const root = document.getElementById('root')
  if (window.Doc && root) {
    const {createOpenEditor} = window.Doc

    editor.value = createOpenEditor(root, {
      input: {},
      darkMode: true,
      image: {
        isCaptureImageURL: () => false,
        uploader: (file, progress, success, failure) => {
          // 验证文件是否为基础二进制类型
          if (typeof file !== 'object' || (file && !('size' in file))) {
            console.error('【编辑器uploader】错误：文件不是二进制对象')
            failure(new Error('图片文件格式错误，无法上传'))
            return
          }

          // 转换文件为标准File对象
          let validFile;
          if (file instanceof File) {
            validFile = file
            if (validFile.lastModified === undefined) {
              validFile = new File([validFile], validFile.name, {
                type: validFile.type,
                lastModified: Date.now()
              })
            }
          } else if (file instanceof Blob) {
            const fileExt = file.type.split('/')[1] || 'png'
            validFile = new File([file], `upload.${fileExt}`, {
              type: file.type,
              lastModified: Date.now()
            })
          } else {
            console.error('【编辑器uploader】错误：文件类型无效（非File/Blob）')
            failure(new Error('无效的图片文件格式'))
            return
          }

          if (!validFile || validFile.size <= 0) {
            console.error('【编辑器uploader】错误：转换后的文件无效')
            failure(new Error('编辑器未获取到有效图片文件'))
            return
          }

          // 调用上传函数
          uploadImage(validFile, {
            onProgress: (percent) => {
              progress(percent)
            },
            onSuccess: (url) => {
              success(url)
            },
            onError: (err) => {
              failure(err)
            }
          })
        }
      },
      formats: {
        paragraph: {
          style: {
            textAlign: 'left',
            lineHeight: props.isMobile ? 1.8 : 1.5,
            maxWidth: '100%',
            wordWrap: 'break-word',
            overflowWrap: 'break-word'
          }
        },
        heading1: {
          style: {
            textAlign: 'left',
            fontSize: props.isMobile ? '24px' : '28px',
            maxWidth: '100%',
            wordWrap: 'break-word'
          }
        },
        heading2: {
          style: {
            textAlign: 'left',
            fontSize: props.isMobile ? '22px' : '24px',
            maxWidth: '100%',
            wordWrap: 'break-word'
          }
        },
        heading3: {
          style: {
            textAlign: 'left',
            fontSize: props.isMobile ? '20px' : '22px',
            maxWidth: '100%',
            wordWrap: 'break-word'
          }
        },
        heading4: {
          style: {
            textAlign: 'left',
            fontSize: props.isMobile ? '18px' : '20px',
            maxWidth: '100%',
            wordWrap: 'break-word'
          }
        },
        heading5: {
          style: {
            textAlign: 'left',
            fontSize: props.isMobile ? '16px' : '18px',
            maxWidth: '100%',
            wordWrap: 'break-word'
          }
        },
        heading6: {
          style: {
            textAlign: 'left',
            fontSize: props.isMobile ? '15px' : '16px',
            maxWidth: '100%',
            wordWrap: 'break-word'
          }
        }
      }
    })

    // 设置初始内容
    editor.value.setDocument(
        'text/lake',
        props.modelValue && props.modelValue.trim() !== ''
            ? props.modelValue
            : `<p style="text-align: left; line-height: ${props.isMobile ? 1.8 : 1.5}; max-width: 100%; word-wrap: break-word; overflow-wrap: break-word;"><span style="color: rgb(182,182,182)">在此区域编辑</span></p>`
    )

    // 内容变化监听
    editor.value.on('contentchange', () => {
      const content = editor.value.getDocument('text/lake')
      emit('update:modelValue', content)
    })

    // 监听编辑器容器大小变化
    const resizeObserver = new ResizeObserver(() => {
      handleResize()
    })

    if (root) {
      resizeObserver.observe(root)
    }
  } else {
    console.error('【编辑器init】初始化失败：', {
      windowDocExists: !!window.Doc,
      rootElementExists: !!root
    })
  }
}

// 处理键盘快捷键
const handleKeyDown = (event) => {
  // 检测 Ctrl+S (Windows/Linux) 或 Cmd+S (Mac)
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    // 检查是否在编辑器区域内
    const editorWrapper = document.querySelector('.editor-wrapper')
    const root = document.getElementById('root')
    const isInEditor = (editorWrapper && editorWrapper.contains(event.target)) ||
        (root && root.contains(event.target))

    if (isInEditor) {
      // 阻止浏览器默认保存行为
      event.preventDefault()
      event.stopPropagation()
      // 触发保存请求事件，由父组件处理
      emit('save-request')
    }
  }
}

onMounted(() => {
  nextTick(() => {
    initEditor()
  })
  // 添加键盘事件监听器
  document.addEventListener('keydown', handleKeyDown)
  // 添加窗口大小变化监听器
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // 移除键盘事件监听器
  document.removeEventListener('keydown', handleKeyDown)
  // 移除窗口大小变化监听器
  window.removeEventListener('resize', handleResize)
})

watch(
    () => props.modelValue,
    (newVal) => {
      if (editor.value && newVal !== editor.value.getDocument('text/lake')) {
        editor.value.setDocument('text/lake', newVal || '')
      }
    }
)

// 暴露方法给父组件
const getDocument = (type = 'text/lake') => {
  return editor.value?.getDocument(type)
}

const setDocument = (type = 'text/lake', content) => {
  editor.value?.setDocument(type, content)
}

const getEditorInstance = () => {
  return editor.value
}

// 手动触发自适应调整
const refreshLayout = () => {
  handleResize()
}

// eslint-disable-next-line no-undef
defineExpose({
  getDocument,
  setDocument,
  getEditorInstance,
  refreshLayout
})
</script>

<style scoped>
@import url('https://gw.alipayobjects.com/render/p/yuyan_npm/@alipay_lakex-doc/1.24.0/umd/doc.css');
@import url('https://unpkg.com/antd@4.24.13/dist/antd.css');

.editor-wrapper {
  width: 100%;
  max-width: 100%;
  text-align: left;
  background: linear-gradient(to bottom, #1e1e1e, #1e1e1e);
  box-sizing: border-box;
  overflow: hidden;
  border-radius: 20px;
}

#root {
  min-height: 400px;
  border: 1px solid #1e1e1e;
  border-radius: 4px;
  background-color: #1e1e1e;
  transition: all 0.3s ease;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

/* 基础文本样式统一 - 确保文字完全显示 */
#root .lake-paragraph,
#root [data-type^='heading'] {
  text-align: left !important;
  font-size: 16px !important;
  line-height: 1.5 !important;
  max-width: 100% !important;
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  box-sizing: border-box !important;
}

/* 编辑器内容区域自适应 */
::v-deep .lake-editor-container {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
}

::v-deep .lake-editor-content {
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  word-wrap: break-word !important;
}

/* 图片自适应 */
::v-deep .lake-image {
  max-width: 100% !important;
  height: auto !important;
}

/* 表格自适应 */
::v-deep .lake-table {
  max-width: 100% !important;
  overflow-x: auto !important;
}

::v-deep .lake-table table {
  width: auto !important;
  min-width: 100% !important;
}

/* 代码块自适应 */
::v-deep .lake-code-block {
  max-width: 100% !important;
  overflow-x: auto !important;
}

/* 移动端核心适配样式 */
@media (max-width: 767px) {
  .editor-wrapper {
    background: #fff;
    width: 100vw;
    max-width: 100vw;
    margin-left: -10px;
    margin-right: -10px;
    border-radius: 0px;
  }

  #root {
    min-height: 350px;
    border: none;
    border-radius: 0;
    margin: 0;
    width: 100%;
    max-width: 100vw;
  }

  /* 深度选择器：优化编辑器工具栏（触控友好） */
  ::v-deep .lake-toolbar {
    gap: 8px !important;
    max-width: 100vw !important;
    overflow-x: auto !important;
  }

  ::v-deep .lake-toolbar-button {
    width: 40px !important;
    height: 40px !important;
    font-size: 18px !important;
    flex-shrink: 0 !important;
  }

  /* 优化文本样式，适配移动端阅读 */
  ::v-deep .lake-paragraph {
    font-size: 16px !important;
    line-height: 1.8 !important;
    margin: 12px 0 !important;
    word-break: break-word !important;
  }

  /* 标题样式适配 */
  ::v-deep [data-type="heading1"] {
    font-size: 24px !important;
    margin: 20px 0 12px !important;
  }

  ::v-deep [data-type="heading2"] {
    font-size: 22px !important;
    margin: 18px 0 10px !important;
  }

  ::v-deep [data-type^="heading"] {
    line-height: 1.6 !important;
    word-break: break-word !important;
  }

  /* 图片预览自适应 */
  ::v-deep .lake-image {
    max-width: 100vw !important;
    height: auto !important;
    margin: 15px auto !important;
  }

  /* 优化输入区域触控体验 */
  ::v-deep .lake-editor-content {
    min-height: 300px !important;
  }

  /* 去掉多余边框和阴影，适配移动端简洁风格 */
  ::v-deep .lake-editor-container {
    border: none !important;
    box-shadow: none !important;
    max-width: 100vw !important;
  }

  /* 移动端横向滚动优化 */
  ::v-deep .lake-editor-content > * {
    max-width: 100% !important;
    overflow-x: hidden !important;
  }
}

/* 平板适配（过渡效果） */
@media (min-width: 768px) and (max-width: 1023px) {




  ::v-deep .lake-paragraph {
    font-size: 16px !important;
    line-height: 1.6 !important;
    max-width: 100% !important;
  }

  ::v-deep .lake-toolbar {
    max-width: 100% !important;
  }
}

/* 大屏适配 */
@media (min-width: 1024px) {
  .editor-wrapper {
    max-width: 100%;
    margin: 0 auto;
  }

  #root {
    max-width: 100%;
    margin: 0 auto;
  }
}

/* 超小屏手机优化 */
@media (max-width: 320px) {




  ::v-deep .lake-paragraph {
    font-size: 15px !important;
    line-height: 1.9 !important;
  }

  ::v-deep [data-type="heading1"] {
    font-size: 22px !important;
  }
}

/* 确保所有内容都能完全显示 */
::v-deep * {
  box-sizing: border-box !important;
  max-width: 100% !important;
}

/* 防止长单词和URL溢出 */
::v-deep .lake-editor-content {
  word-wrap: break-word !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
}
</style>