<template>
  <div class="editor-container" :style="{ transform: `scale(${scaleRatio})`, transformOrigin: 'top center' }">
    <el-form
        :model="form"
        ref="articleForm"
        label-width="100px"
        :rules="rules"
        class="article-form"
    >
      <div class="form-header">
        <h2>{{ form.id ? "编辑文章" : "新建文章" }}</h2>
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
            style="color: #1e1e1e"
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
              :src="$img(form.coverUrl)"
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

      <!-- 分类 -->
      <el-form-item label="分类" prop="categoryId" class="form-item-mobile">
        <div class="category-selector-responsive">
          <el-select v-model="form.categoryId" placeholder="请选择文章分类" size="large" clearable>
            <el-option label="未分类" :value="null"></el-option>
            <el-option
                v-for="category in categories"
                :key="category.id"
                :label="category.name"
                :value="category.id"
            ></el-option>
          </el-select>

          <el-button
              type="primary"
              size="small"
              class="create-category-btn"
              @click="openCreateCategoryDialog"
          >
            新建分类
          </el-button>
        </div>
      </el-form-item>

      <MarkdownEditor
          ref="markdownEditor"
          v-model="form.content"
          @save-request="submitForm"
          class="editor-css"
      />
    </el-form>
  </div>

  <!-- 新建分类对话框 -->
  <el-dialog
      title="新建分类"
      v-model="showCreateCategoryDialog"
      width="360px"
      :close-on-click-modal="false"
  >
    <el-form
        :model="newCategoryForm"
        ref="newCategoryForm"
        label-width="80px"
        :rules="newCategoryRules"
    >
      <el-form-item label="分类名称" prop="name">
        <el-input
            v-model="newCategoryForm.name"
            placeholder="请输入分类名称"
            maxlength="100"
            show-word-limit
        ></el-input>
      </el-form-item>

      <el-form-item label="描述">
        <el-input
            type="textarea"
            v-model="newCategoryForm.description"
            placeholder="请输入分类描述（可选）"
            maxlength="500"
            show-word-limit
            :rows="3"
        ></el-input>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="showCreateCategoryDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateCategory">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import MarkdownEditor from "@/components/Article/MarkdownEditor.vue";
import axios from "axios";

export default {
  name: "ReleaseComponent",
  components: { MarkdownEditor },
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
      categories: [],
      rules: {
        title: [
          { required: true, message: "请输入文章标题", trigger: "blur" },
          { max: 200, message: "标题长度不能超过200个字符", trigger: "blur" }
        ],
        content: [{ required: true, message: "请输入文章正文", trigger: "change" }],
        status: [{ required: true, message: "请选择文章状态", trigger: "change" }],
        categoryId: [{ required: false, message: "请选择分类", trigger: "change" }]
      },
      scaleRatio: 1.0,
      scaleStep: 0.1,
      showCreateCategoryDialog: false,
      newCategoryForm: {
        name: "",
        description: ""
      },
      newCategoryRules: {
        name: [
          { required: true, message: "请输入分类名称", trigger: "blur" },
          { max: 100, message: "分类名称长度不能超过100个字符", trigger: "blur" }
        ]
      }
    };
  },
  watch: {
    currentArticle: {
      immediate: true,
      handler(val) {
        if (val) {
          if (this.categories.length) {
            this.setFormData(val);
          }
        } else {
          this.form = this.getDefaultForm();
        }
      }
    }
  },
  async mounted() {
    document.addEventListener('keydown', this.handleKeyDown);
    document.addEventListener('wheel', this.handleWheel, { passive: false });

    await this.loadCategories();

    if (this.currentArticle) {
      this.setFormData(this.currentArticle);
    }
  },
  beforeUnmount() {
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

    setFormData(article) {
      this.form = {
        id: article.id || null,
        title: article.title || "",
        coverUrl: article.coverUrl || "",
        status: article.status || "DRAFT",
        content: article.content || "",
        summary: article.summary || article.abstract || article.description || "",
        categoryId: article.category != null ? article.category : null // 核心修改：确保未分类也能打开
      };
      console.log("文章数据：", this.form);
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
        this.$emit("save-success", { ...this.form });
      });
    },

    handleCancel() {
      this.$emit("cancel");
    },

    handleKeyDown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        event.preventDefault();
        event.stopPropagation();
        this.submitForm();
      }
    },

    handleWheel(event) {
      if (event.ctrlKey || event.metaKey) {
        event.preventDefault();
        event.stopPropagation();
        const delta = event.deltaY > 0 ? -this.scaleStep : this.scaleStep;
        this.scaleRatio = Math.min(Math.max(this.scaleRatio + delta, 0.5), 2.0);
      }
    },

    async loadCategories() {
      try {
        const res = await axios.get("/api/categories");
        if (res && res.data && res.data.code === 200) {
          this.categories = Array.isArray(res.data.data) ? res.data.data : [];
        } else {
          this.$message.error("获取分类列表失败：" + (res?.data?.message || "未知错误"));
        }
      } catch (error) {
        this.$message.error("获取分类列表失败：" + (error?.message || "网络错误"));
        console.error("加载分类出错：", error);
      }
    },

    openCreateCategoryDialog() {
      this.newCategoryForm = { name: "", description: "" };
      this.$refs.newCategoryForm && this.$refs.newCategoryForm.resetFields();
      this.showCreateCategoryDialog = true;
    },

    async handleCreateCategory() {
      this.$refs.newCategoryForm.validate(async (valid) => {
        if (!valid) return;
        try {
          const res = await axios.post("/api/categories", this.newCategoryForm);
          if (res && res.data && res.data.code === 200) {
            this.$message.success("分类创建成功");
            this.showCreateCategoryDialog = false;
            await this.loadCategories();
            if (res.data.data && res.data.data.id !== undefined) {
              this.form.categoryId = res.data.data.id;
            }
          } else {
            this.$message.error("创建分类失败：" + (res?.data?.message || "未知错误"));
          }
        } catch (error) {
          this.$message.error("创建分类失败：" + (error?.message || "网络错误"));
          console.error("创建分类出错：", error);
        }
      });
    }
  }
};
</script>

<style scoped>
.editor-container {
  overflow: visible;
  padding: 20px;
  height: 100%;
  position: relative;
  transition: transform 0.2s ease;
  background-color: #0a0a0a;
  color: rgba(255, 255, 255, 0.9);
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-weight: 300;
  letter-spacing: 0.3px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.editor-container::-webkit-scrollbar { display: none; }
.article-form { 
  max-width: 800px; 
  margin: 0 auto; 
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 4px;
  background-color: rgba(10, 10, 10, 0.5);
}
.form-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 20px; 
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 15px;
}
.form-header h2 { 
  color: rgba(255, 255, 255, 0.9);
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.form-header-actions { 
  display: flex; 
  gap: 10px; 
}

/* 金属风格按钮 */
.form-header-actions .el-button {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.3s ease !important;
}

.form-header-actions .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.form-header-actions .el-button:hover::before {
  left: 100%;
}

.form-header-actions .el-button--primary {
  border-color: rgba(79, 195, 247, 0.5) !important;
  color: rgba(79, 195, 247, 0.9) !important;
}

.form-header-actions .el-button--primary::before {
  background: linear-gradient(90deg, transparent, rgba(79, 195, 247, 0.3), transparent);
}

.form-header-actions .el-button:hover {
  border-color: rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
}

.form-header-actions .el-button--primary:hover {
  border-color: rgba(79, 195, 247, 0.8) !important;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.3) !important;
}

/* 表单项样式 */
::v-deep .el-form-item__label {
  color: rgba(255, 255, 255, 0.7) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  font-size: 0.85rem !important;
}

::v-deep .el-input__wrapper {
  background-color: rgba(20, 20, 20, 0.5) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  transition: all 0.3s ease !important;
}

::v-deep .el-input__wrapper:hover {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

::v-deep .el-input__wrapper.is-focus {
  border-color: rgba(79, 195, 247, 0.5) !important;
  box-shadow: 0 0 0 1px rgba(79, 195, 247, 0.3) !important;
}

::v-deep .el-input__inner {
  color: rgba(255, 255, 255, 0.9) !important;
  background-color: transparent !important;
  font-weight: 300 !important;
}

::v-deep .el-textarea__inner {
  background-color: rgba(20, 20, 20, 0.5) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0 !important;
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 300 !important;
  transition: all 0.3s ease !important;
}

::v-deep .el-textarea__inner:hover {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

::v-deep .el-textarea__inner:focus {
  border-color: rgba(79, 195, 247, 0.5) !important;
  box-shadow: 0 0 0 1px rgba(79, 195, 247, 0.3) !important;
}

/* 选择器样式 */
::v-deep .el-select .el-input__wrapper {
  background-color: rgba(20, 20, 20, 0.5) !important;
}

::v-deep .el-select-dropdown {
  background-color: #0a0a0a !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
}

::v-deep .el-select-dropdown__item {
  color: rgba(255, 255, 255, 0.8) !important;
  font-weight: 300 !important;
}

::v-deep .el-select-dropdown__item:hover {
  background-color: rgba(79, 195, 247, 0.1) !important;
  color: rgba(79, 195, 247, 0.9) !important;
}

::v-deep .el-select-dropdown__item.selected {
  background-color: rgba(79, 195, 247, 0.2) !important;
  color: rgba(79, 195, 247, 0.9) !important;
  font-weight: 400 !important;
}

/* 上传组件样式 */
.avatar-uploader {
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0 !important;
  background-color: rgba(20, 20, 20, 0.5) !important;
  transition: all 0.3s ease !important;
}

.avatar-uploader:hover {
  border-color: rgba(255, 255, 255, 0.2) !important;
}

.upload-placeholder {
  color: rgba(255, 255, 255, 0.6) !important;
  font-weight: 300 !important;
}

.upload-tip {
  color: rgba(255, 255, 255, 0.5) !important;
  font-size: 0.8rem !important;
  margin-top: 5px !important;
}

.delete-cover {
  color: rgba(255, 107, 107, 0.8) !important;
  font-weight: 300 !important;
  margin-top: 5px !important;
}

.delete-cover:hover {
  color: rgba(255, 107, 107, 1) !important;
}

/* 分类选择器响应式样式 */
.category-selector-responsive {
  display: flex;
  gap: 10px;
  align-items: center;
}

.create-category-btn {
  background: transparent !important;
  border: 1px solid rgba(79, 195, 247, 0.5) !important;
  color: rgba(79, 195, 247, 0.9) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.3s ease !important;
}

.create-category-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(79, 195, 247, 0.3), transparent);
  transition: left 0.5s;
}

.create-category-btn:hover::before {
  left: 100%;
}

.create-category-btn:hover {
  border-color: rgba(79, 195, 247, 0.8) !important;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.3) !important;
}

/* 对话框样式 */
::v-deep .el-dialog {
  background-color: #0a0a0a !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7) !important;
}

::v-deep .el-dialog__header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

::v-deep .el-dialog__title {
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
}

::v-deep .el-dialog__footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.dialog-footer .el-button {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.3s ease !important;
}

.dialog-footer .el-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.dialog-footer .el-button:hover::before {
  left: 100%;
}

.dialog-footer .el-button--primary {
  border-color: rgba(79, 195, 247, 0.5) !important;
  color: rgba(79, 195, 247, 0.9) !important;
}

.dialog-footer .el-button--primary::before {
  background: linear-gradient(90deg, transparent, rgba(79, 195, 247, 0.3), transparent);
}

.dialog-footer .el-button:hover {
  border-color: rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
}

.dialog-footer .el-button--primary:hover {
  border-color: rgba(79, 195, 247, 0.8) !important;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.3) !important;
}

/* 编辑器样式 */
.editor-css {
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0 !important;
  background-color: rgba(20, 20, 20, 0.5) !important;
}
</style>
