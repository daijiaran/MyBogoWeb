<template>
  <div class="editor-wrapper">
    <div id="root" class="ne-doc-major-editor"></div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, nextTick, ref, watch } from 'vue'

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
const uploadImage = async (file, { onSuccess, onError }) => {
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
    const response = await fetch('/api/upload/image', {
      method: 'POST',
      body: formData,
      signal: abortController.signal,
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
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

// 初始化编辑器
const initEditor = () => {
  const root = document.getElementById('root')
  if (window.Doc && root) {
    const { createOpenEditor } = window.Doc

    editor.value = createOpenEditor(root, {
      input: {},
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
        paragraph: { style: { textAlign: 'left', lineHeight: props.isMobile ? 1.8 : 1.5 } }, // 移动端增大行高
        heading1: { style: { textAlign: 'left', fontSize: props.isMobile ? '24px' : '28px' } },
        heading2: { style: { textAlign: 'left', fontSize: props.isMobile ? '22px' : '24px' } },
        heading3: { style: { textAlign: 'left', fontSize: props.isMobile ? '20px' : '22px' } },
        heading4: { style: { textAlign: 'left', fontSize: props.isMobile ? '18px' : '20px' } },
        heading5: { style: { textAlign: 'left', fontSize: props.isMobile ? '16px' : '18px' } },
        heading6: { style: { textAlign: 'left', fontSize: props.isMobile ? '15px' : '16px' } }
      }
    })

    // 设置初始内容
    editor.value.setDocument(
        'text/lake',
        props.modelValue && props.modelValue.trim() !== ''
            ? props.modelValue
            : `<p style="text-align: left; line-height: ${props.isMobile ? 1.8 : 1.5};"><span style="color: rgb(182,182,182)">在此区域编辑</span></p>`
    )

    // 内容变化监听
    editor.value.on('contentchange', () => {
      const content = editor.value.getDocument('text/lake')
      emit('update:modelValue', content)
    })
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
})

onUnmounted(() => {
  // 移除键盘事件监听器
  document.removeEventListener('keydown', handleKeyDown)
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

// eslint-disable-next-line no-undef
defineExpose({
  getDocument,
  setDocument,
  getEditorInstance
})
</script>

<style scoped>
@import url('https://gw.alipayobjects.com/render/p/yuyan_npm/@alipay_lakex-doc/1.24.0/umd/doc.css');
@import url('https://unpkg.com/antd@4.24.13/dist/antd.css');

.editor-wrapper {
  width: 100%;
  text-align: left;
  /* 冷调背景呼应整体风格 */
  background: linear-gradient(to bottom, #f8fafc, #eef2f6);
}

#root {
  min-height: 400px;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  padding: 20px;
  background-color: #fff;
  transition: all 0.3s ease;
}

/* 基础文本样式统一 */
#root .lake-paragraph,
#root [data-type^='heading'] {
  text-align: left !important;
  font-size: 16px !important;
  line-height: 1.5 !important;
}

/* 移动端核心适配样式 */
@media (max-width: 767px) {
  .editor-wrapper {
    padding: 0 10px;
    background: #fff; /* 移动端去掉渐变，避免与编辑器背景冲突 */
  }

  #root {
    min-height: 350px; /* 适配移动端屏幕高度 */
    border: none; /* 去掉边框，更简洁 */
    border-radius: 0; /* 全屏无圆角 */
    padding: 15px 10px; /* 调整内边距，避免拥挤 */
    margin: 0;
  }

  /* 深度选择器：优化编辑器工具栏（触控友好） */
  ::v-deep .lake-toolbar {
    padding: 8px 10px !important;
    gap: 8px !important; /* 增大工具栏按钮间距 */
  }

  ::v-deep .lake-toolbar-button {
    width: 40px !important; /* 增大按钮点击区域 */
    height: 40px !important;
    font-size: 18px !important; /* 增大图标大小 */
  }

  /* 优化文本样式，适配移动端阅读 */
  ::v-deep .lake-paragraph {
    font-size: 16px !important;
    line-height: 1.8 !important; /* 增大行高，提升阅读体验 */
    margin: 12px 0 !important; /* 调整段落间距 */
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
  }

  /* 图片预览自适应 */
  ::v-deep .lake-image {
    max-width: 100% !important; /* 图片不超出屏幕宽度 */
    height: auto !important;
    margin: 15px auto !important;
  }

  /* 优化输入区域触控体验 */
  ::v-deep .lake-editor-content {
    min-height: 300px !important;
    padding-bottom: 20px !important; /* 避免内容被底部遮挡 */
  }

  /* 去掉多余边框和阴影，适配移动端简洁风格 */
  ::v-deep .lake-editor-container {
    border: none !important;
    box-shadow: none !important;
  }
}

/* 平板适配（过渡效果） */
@media (min-width: 768px) and (max-width: 1023px) {
  #root {
    min-height: 450px;
    padding: 20px;
  }

  ::v-deep .lake-paragraph {
    font-size: 16px !important;
    line-height: 1.6 !important;
  }
}
</style>