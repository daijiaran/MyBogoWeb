<template>
  <div class="editor-container" :style="{ transform: `scale(${scaleRatio})`, transformOrigin: 'top center' }">
    <!-- 移动端返回按钮 -->
    <el-button
        type="text"
        class="mobile-back-btn"
        @click="handleCancel"
        v-if="isMobile"
    >
      <i class="el-icon-back"></i> 返回
    </el-button>

    <el-form
        :model="form"
        ref="articleForm"
        label-width="100px"
        :rules="rules"
        class="article-form"
    >
      <div class="form-header">
        <h2>{{ form.id ? "编辑文章" : "新建文章" }}</h2>
        <!-- 移动端隐藏头部操作栏，移到底部 -->
        <div class="form-header-actions" v-if="!isMobile">
          <el-button type="text" @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="submitForm">保存</el-button>
        </div>
      </div>

      <el-form-item label="标题" prop="title" class="form-item-mobile">
        <el-input
            v-model="form.title"
            placeholder="请输入文章标题"
            maxlength="200"
            show-word-limit
            size="large"
        ></el-input>
      </el-form-item>

      <el-form-item label="封面图" prop="coverUrl" class="form-item-mobile">
        <el-upload
            class="avatar-uploader"
            action="/api/upload/image"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleCoverUploadSuccess"
            :before-upload="beforeCoverUpload"
            accept="image/jpeg,image/png,image/webp"
        >
          <img
              v-if="form.coverUrl"
              :src="form.coverUrl"
              class="cover-preview"
              alt="封面图"
          />
          <div v-else class="upload-placeholder">
            <i class="el-icon-plus avatar-uploader-icon"></i>
            <div class="upload-tip">点击上传封面图（支持JPG、PNG、WebP）</div>
          </div>
        </el-upload>
        <el-button
            v-if="form.coverUrl"
            size="mini"
            type="text"
            class="delete-cover"
            @click="handleRemoveCover"
        >
          <i class="el-icon-delete"></i> 移除封面
        </el-button>
      </el-form-item>

      <el-form-item label="摘要" prop="summary" class="form-item-mobile">
        <el-input
            type="textarea"
            v-model="form.summary"
            placeholder="请输入文章摘要（简要介绍文章内容）"
            maxlength="300"
            show-word-limit
            size="large"
            :rows="4"
        ></el-input>
      </el-form-item>

      <el-form-item label="状态" prop="status" class="form-item-mobile">
        <el-select
            v-model="form.status"
            placeholder="请选择文章状态"
            size="large"
        >
          <el-option label="草稿" value="DRAFT"></el-option>
          <el-option label="已发布" value="PUBLISHED"></el-option>
          <el-option label="已下架" value="DISABLED"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="正文" prop="content" class="form-item-mobile markdown-editor-item">
        <MarkdownEditor
            ref="markdownEditor"
            v-model="form.content"
            :is-mobile="isMobile"
            :min-height="isMobile ? 350 : 500"
            @save-request="submitForm"
        />
      </el-form-item>
    </el-form>

    <!-- 移动端底部固定操作栏 -->
    <div class="mobile-footer-actions" v-if="isMobile">
      <el-button
          type="default"
          @click="handleCancel"
          class="footer-btn cancel-btn"
      >
        取消
      </el-button>
      <el-button
          type="primary"
          @click="submitForm"
          class="footer-btn submit-btn"
      >
        保存
      </el-button>
    </div>
  </div>
</template>

<script>
import MarkdownEditor from "@/components/MarkdownEditor.vue";

export default {
  name: "ReleaseComponent",
  components: {MarkdownEditor},
  props: {
    currentArticle: {
      type: Object,
      default: () => null
    },
    isMobile: {
      type: Boolean,
      default: false
    },
    uploadHeaders: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      form: {
        id: null,
        title: "",
        coverUrl: "",
        status: "DRAFT",
        categoryId: null,
        summary: "",
        content: ""
      },
      rules: {
        title: [
          {required: true, message: "请输入文章标题", trigger: "blur"},
          {max: 200, message: "标题长度不能超过200个字符", trigger: "blur"}
        ],
        content: [{required: true, message: "请输入文章正文", trigger: "change"}],
        status: [{required: true, message: "请选择文章状态", trigger: "change"}]
      },
      // 缩放比例，默认100%，范围0.5-2.0
      scaleRatio: 1.0,
      // 缩放步长
      scaleStep: 0.1
    };
  },
  watch: {
    currentArticle: {
      immediate: true,
      handler(val) {
        if (val) {
          // 确保摘要字段正确映射（兼容可能的字段名差异）
          this.form = {
            ...val,
            summary: val.summary || val.abstract || val.description || ''
          };
          console.log('ReleaseComponent 接收到的文章数据：', val);
          console.log('ReleaseComponent 摘要字段值：', this.form.summary);
        } else {
          this.form = this.getDefaultForm();
        }
      }
    }
  },
  mounted() {
    // 添加键盘事件监听器
    document.addEventListener('keydown', this.handleKeyDown);
    // 添加鼠标滚轮事件监听器
    document.addEventListener('wheel', this.handleWheel, {passive: false});
  },
  beforeUnmount() {
    // 移除事件监听器
    document.removeEventListener('keydown', this.handleKeyDown);
    document.removeEventListener('wheel', this.handleWheel);
  },
  methods: {
    getDefaultForm() {
      return {
        id: null,
        title: "",
        coverUrl: "",
        status: "DRAFT",
        categoryId: null,
        summary: "",
        content: ""
      };
    },

    handleCoverUploadSuccess(res) {
      if (res.code === 200) {
        this.form.coverUrl = res.data.url;
        this.$message.success("封面上传成功");
      } else {
        this.$message.error("封面上传失败：" + res.message);
      }
    },

    beforeCoverUpload(file) {
      const okType = ["image/jpeg", "image/png", "image/webp"].includes(file.type);
      if (!okType) {
        this.$message.error("仅支持 JPG、PNG、WebP 格式的图片！");
        return false;
      }
      if (file.size / 1024 / 1024 >= 10) {
        this.$message.error("封面图大小不能超过 10MB！");
        return false;
      }
      return true;
    },

    handleRemoveCover() {
      this.form.coverUrl = "";
    },

    submitForm() {
      this.$refs.articleForm.validate((valid) => {
        if (!valid) return;
        this.$emit("save-success", {...this.form});
      });
    },

    handleCancel() {
      this.$emit("cancel");
    },

    // 处理键盘快捷键
    handleKeyDown(event) {
      // 检测 Ctrl+S (Windows/Linux) 或 Cmd+S (Mac)
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        // 阻止浏览器默认保存行为
        event.preventDefault();
        event.stopPropagation();
        this.submitForm();
      }
    },

    // 处理鼠标滚轮事件（Ctrl+滚轮缩放）
    handleWheel(event) {
      // 只在按下Ctrl键时触发缩放
      if (event.ctrlKey || event.metaKey) {
        // 阻止浏览器默认的缩放行为
        event.preventDefault();
        event.stopPropagation();

        // 滚轮向上滚动：放大，向下滚动：缩小
        const delta = event.deltaY > 0 ? -this.scaleStep : this.scaleStep;

        // 更新缩放比例，限制在0.5-2.0之间
        this.scaleRatio = Math.min(Math.max(this.scaleRatio + delta, 0.5), 2.0);

        // 可选：显示当前缩放比例提示
      }
    }
  }
};
</script>

<style scoped>
.editor-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  position: relative; /* 为底部操作栏定位做准备 */
  transition: transform 0.2s ease; /* 平滑缩放过渡 */
}

.editor-container::-webkit-scrollbar {
  display: none;
}

.article-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-header-actions {
  display: flex;
  gap: 10px;
}

.cover-preview {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #eee;
}

.upload-placeholder {
  width: 200px;
  height: 120px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #86909c;
  cursor: pointer;
  transition: border-color 0.2s;
}

.upload-placeholder:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 12px;
  text-align: center;
  padding: 0 10px;
}

.delete-cover {
  margin-top: 8px;
  color: #f56c6c;
  padding-left: 0;
}

.markdown-editor-item {
  margin-bottom: 0 !important;
}

/* 移动端专属样式 - 重点优化 */
@media (max-width: 767px) {
  .editor-container {
    padding: 15px;
    padding-bottom: 80px; /* 给底部操作栏留空间 */
    /* 移动端默认不允许缩放，保持100% */
    transform: scale(1.0) !important;
  }

  /* 移动端返回按钮 */
  .mobile-back-btn {
    position: fixed;
    top: 15px;
    left: 15px;
    z-index: 10;
    color: #409eff;
    font-size: 16px;
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .form-item-mobile {
    display: flex;
    flex-direction: column;
    margin-bottom: 25px; /* 增大表单间距，避免拥挤 */
  }

  ::v-deep .form-item-mobile .el-form-item__label {
    width: 100% !important;
    margin-bottom: 12px;
    text-align: left !important; /* 左对齐更符合移动端阅读习惯 */
    font-weight: 600;
    font-size: 16px;
    padding: 0;
  }

  ::v-deep .form-item-mobile .el-form-item__content {
    margin-left: 0 !important;
    border: 1px solid #e4e7ed;
    border-radius: 8px; /* 增大圆角，更美观 */
    padding: 12px;
    background-color: white;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05); /* 轻微阴影，提升质感 */
  }

  /* 增大输入框内边距，提升触控体验 */
  ::v-deep .form-item-mobile .el-input__inner,
  ::v-deep .form-item-mobile .el-textarea__inner {
    padding: 12px 15px !important;
    font-size: 16px !important;
  }

  ::v-deep .form-item-mobile .el-input,
  ::v-deep .form-item-mobile .el-select,
  ::v-deep .form-item-mobile .el-textarea {
    width: 100% !important;
    max-width: 100% !important;
  }

  /* Markdown 编辑器适配 */
  ::v-deep .form-item-mobile.markdown-editor-item .el-form-item__content {
    padding: 0;
    box-shadow: none;
    border: none;
  }

  ::v-deep .form-item-mobile.markdown-editor-item .el-form-item__content > div {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 350px;
  }

  ::v-deep .markdown-editor {
    width: 100% !important;
  }

  ::v-deep .markdown-editor textarea,
  ::v-deep .markdown-editor .preview {
    width: 100% !important;
    box-sizing: border-box !important;
    overflow: auto !important;
    font-size: 16px !important;
    line-height: 1.8 !important; /* 增大行高，提升阅读体验 */
    padding: 15px !important;
  }

  /* 封面图适配 */
  .cover-preview,
  .upload-placeholder {
    width: 100% !important;
    height: auto !important;
    min-height: 180px; /* 增大上传区域，方便点击 */
  }

  .form-header {
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
    margin-top: 10px; /* 给返回按钮留空间 */
  }

  .form-header h2 {
    margin: 0;
    text-align: center;
    width: 100%;
    font-size: 20px;
  }

  /* 底部固定操作栏 */
  .mobile-footer-actions {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    padding: 12px 15px;
    background-color: white;
    border-top: 1px solid #e4e7ed;
    z-index: 9;
    gap: 12px;
  }

  .footer-btn {
    flex: 1;
    height: 48px; /* 增大按钮高度，方便点击 */
    font-size: 16px;
    border-radius: 8px;
  }

  .cancel-btn {
    border: 1px solid #e4e7ed;
  }

  .submit-btn {
    background-color: #409eff;
    border-color: #409eff;
  }

  /* 移除封面按钮优化 */
  .delete-cover {
    font-size: 14px;
    margin-top: 10px;
  }
}

/* 平板适配（可选） */
@media (min-width: 768px) and (max-width: 1023px) {
  .editor-container {
    padding: 20px;
  }

  .article-form {
    max-width: 90%;
  }

  .cover-preview,
  .upload-placeholder {
    width: 250px;
    height: 150px;
  }
}
</style>