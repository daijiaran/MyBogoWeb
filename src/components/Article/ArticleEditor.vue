<template>
  <div class="editor-container">
    <el-form :model="form" ref="articleForm" label-width="100px" :rules="rules">
      <div class="form-header">
        <h2>{{ form.id ? '编辑文章' : '新建文章' }}</h2>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </div>

      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" />
      </el-form-item>

      <el-form-item label="封面图" prop="coverUrl">
        <el-upload
            action="/api/upload/image"
            :headers="getUploadHeaders()"
            :show-file-list="false"
            :on-success="handleCoverUploadSuccess"
        >
          <img v-if="form.coverUrl" :src="$img(form.coverUrl)" class="cover-preview" />
          <div v-else class="upload-placeholder">上传封面</div>
        </el-upload>
      </el-form-item>

      <el-form-item label="摘要" prop="summary">
        <el-input type="textarea" v-model="form.summary" />
      </el-form-item>

      <el-form-item label="状态" prop="status">
        <el-select v-model="form.status">
          <el-option label="草稿" value="DRAFT" />
          <el-option label="已发布" value="PUBLISHED" />
        </el-select>
      </el-form-item>

      <el-form-item label="正文" prop="content">
        <MarkdownEditor v-model="form.content" />
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import MarkdownEditor from '@/components/Article/MarkdownEditor.vue'
import axios from 'axios'

export default {
  name: 'ArticleEditor',
  components: { MarkdownEditor },
  props: { article: Object },
  data() {
    return {
      form: {},
      rules: { title: [{ required: true, message: '请输入标题', trigger: 'blur' }] },
    }
  },
  watch: {
    article: {
      immediate: true,
      handler(val) {
        this.form = { ...val }
      },
    },
  },
  methods: {
    getUploadHeaders() {
      const token = localStorage.getItem('token')
      return token ? { Authorization: `Bearer ${token}` } : {}
    },
    handleCoverUploadSuccess(res) {
      if (res.code === 200) this.form.coverUrl = res.data.url
    },
    submitForm() {
      this.$refs.articleForm.validate(async (valid) => {
        if (!valid) return
        const res = this.form.id
            ? await axios.put(`/api/articles/${this.form.id}`, this.form)
            : await axios.post('/api/articles', this.form)
        if (res.data.code === 200) {
          this.$message.success('保存成功')
          this.$emit('save', res.data.data)
        }
      })
    },
  },
}
</script>

<style scoped>
.editor-container {
  padding: 20px;
  background: #1e1e1e;
  flex: 1;
  overflow-y: auto;
}
.cover-preview {
  width: 200px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
}
.upload-placeholder {
  width: 200px;
  height: 120px;
  border: 1px dashed #555;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  background-color: #2d2d2d;
}
</style>
