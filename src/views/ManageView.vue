<template>
  <div class="Main">
    <div class="manage-container">
      <div class="split-layout" ref="splitLayout">
        <!-- 移动端返回按钮 -->
        <div class="mobile-back-btn" @click="showList = true" v-if="isMobile && !showList">
          <ElIcon>
            <ArrowLeft />
          </ElIcon>
          <span>返回列表</span>
        </div>

        <!-- 左侧文章列表 -->
        <div
            class="sidebar"
            :class="{ 'mobile-hidden': isMobile && !showList }"
            :style="{
            width: sidebarWidth + 'px',
            transform: isCollapsed ? `translateX(-${sidebarWidth}px)` : 'translateX(0)',
            transition: 'transform 0.3s ease'
          }"
        >

          <div class="article-container">
            <!-- 上方：文章列表标题 + 数量 + 全选 + 批量删除 -->
            <div class="article-header">
              <div class="list-header-left">
                <el-checkbox
                    v-model="isAllSelected"
                    @change="handleSelectAll"
                    :disabled="articleList.length === 0"
                    class="all-select-checkbox"
                ></el-checkbox>
                <h3 class="list-title">文章列表</h3>
              </div>
              <div class="list-header-right">
                <span class="list-count">{{ articleList.length + "/" + totalArticles }} 篇文章</span>
                <el-button
                    v-if="selectedArticleIds.length > 0"
                    class="batch-delete-btn"
                    type="danger"
                    icon="el-icon-delete"
                    size="small"
                    @click="handleBatchDelete"
                    :loading="isBatchDeleting"
                    :disabled="isBatchDeleting"
                >
                  批量删除 ({{ selectedArticleIds.length }})
                </el-button>
              </div>
            </div>

            <!-- 下方：搜索框 + 新建文章按钮 -->
            <div class="search-and-create">
              <el-input
                  v-model="searchKeyword"
                  placeholder="搜索文章"
                  clearable
                  size="small"
                  @keyup.enter="handleSearch"
              ></el-input>
              <el-button
                  class="create-btn"
                  type="primary"
                  icon="el-icon-plus"
                  size="small"
                  @click="handleCreateArticle"
              >
                新建文章
              </el-button>
            </div>
          </div>

          <div class="article-list" @scroll="handleScroll">
            <!-- 空状态处理 -->
            <div v-if="articleList.length === 0 && !isLoading" class="empty-state">
              <div class="empty-icon">
                <i class="el-icon-file-text-outline"></i>
              </div>
              <p class="empty-text">暂无文章数据</p>
              <el-button
                  size="small"
                  type="text"
                  @click="handleCreateArticle"
              >
                立即创建
              </el-button>
            </div>

            <div class="articles-grid">
              <!-- 文章卡片循环 -->
              <div
                  v-for="(item, index) in articleList"
                  :key="item.id"
                  class="article-card"
                  :class="{
                  active: currentEditingArticle && currentEditingArticle.id === item.id,
                  'has-cover': item.coverUrl
                }"
                  @click="handleSelectArticle(item, $event)"
                  :data-article-index="articleList.length - index - 1"
              >
                <!-- 选择复选框 -->
                <el-checkbox
                    v-model="selectedArticleIds"
                    :label="item.id"
                    @change="handleSingleSelect"
                    class="article-checkbox"
                    @click.stop
                ></el-checkbox>

                <!-- 封面图 -->
                <div v-if="item.coverUrl" class="article-cover">
                  <img :src="$img(item.coverUrl)" :alt="item.title" class="cover-img">
                </div>

                <div class="article-info">
                <span class="article-title" :title="item.title">
                  {{ truncateTitle(item.title, 24) }}
                </span>

                  <!-- 状态标签 -->
                  <div class="article-meta">
                    <el-tag
                        :type="getStatusTagType(item.status)"
                        size="mini"
                        class="status-tag"
                    >
                      {{ formatStatus(item.status) }}
                    </el-tag>

                    <!-- 时间信息 -->
                    <span class="article-date" v-if="item.updateTime">
                    {{ formatDate(item.updateTime) }}
                  </span>
                  </div>
                </div>

                <!-- 操作按钮组 -->
                <div class="article-actions">
                  <el-button
                      type="text"
                      size="small"
                      icon="el-icon-delete"
                      class="delete-btn"
                      @click.stop="handleDelete(item.id)"
                      title="删除"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 加载状态提示 -->
            <div class="load-more">
              <el-loading
                  v-if="isLoading"
                  spinner="el-icon-loading"
                  text="加载中..."
                  size="small"
              ></el-loading>
              <p v-else-if="!hasMore && articleList.length > 0">已加载全部文章</p>
            </div>
          </div>

        </div>
        <!-- 分隔线 - 可拖动 -->
        <div
            class="divider"
            @mousedown="startDrag"
            :style="{
            left: isCollapsed ? '0' : `${sidebarWidth}px`,
            height: '100%',
            display: isMobile ? 'none' : 'block'
          }"
        ></div>

        <!-- 折叠/展开按钮 -->
        <div
            class="toggle-btn"
            @click="toggleSidebar"
            :style="{
            left: isCollapsed ? '6px' : `${sidebarWidth}px`,
            top: '50%',
            transform: 'translateY(-50%)',
            display: isMobile ? 'none' : 'block'
          }"
        >
          <ElIcon v-if="isCollapsed">
            <ArrowRight />
          </ElIcon>
          <ElIcon v-else>
            <ArrowLeft />
          </ElIcon>
        </div>

        <!-- 右侧编辑区 -->
        <div
            class="editor-area"
            :class="{ 'mobile-hidden': isMobile && showList }"
            :style="{
            left: isCollapsed ? '6px' : `${sidebarWidth + 6}px`
          }"
        >
          <div v-if="!currentEditingArticle && !isMobile" class="placeholder">
            <p>请在左侧选择文章或新建一篇</p>
          </div>

          <div v-else class="editor-container">
            <el-form
                :model="form"
                ref="articleForm"
                label-width="100px"
                :rules="rules"
                class="article-form"
            >
              <div class="form-header">
                <h2>{{ form.id ? "编辑文章" : "新建文章" }}</h2>
                <el-button type="primary" @click="submitForm">保存</el-button>
              </div>

              <el-form-item label="标题" prop="title" class="form-item-mobile">
                <el-input
                    v-model="form.title"
                    placeholder="请输入文章标题"
                    maxlength="200"
                    show-word-limit
                ></el-input>
              </el-form-item>

              <el-form-item label="封面图" prop="coverUrl" class="form-item-mobile">
                <el-upload
                    class="avatar-uploader"
                    action="/api/upload/image"
                    :headers="getUploadHeaders()"
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
                    placeholder="请输入文章摘要"
                    maxlength="300"
                    show-word-limit
                ></el-input>
              </el-form-item>

              <el-form-item label="状态" prop="status" class="form-item-mobile">
                <el-select v-model="form.status" placeholder="请选择文章状态">
                  <el-option label="草稿" value="DRAFT"></el-option>
                  <el-option label="已发布" value="PUBLISHED"></el-option>
                  <el-option label="已下架" value="DISABLED"></el-option>
                </el-select>
              </el-form-item>

              <el-form-item label="正文" prop="content" class="form-item-mobile markdown-editor-item">
                <MarkdownEditor ref="markdownEditor" v-model="form.content" :is-mobile="isMobile" />
              </el-form-item>
            </el-form>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import _ from "lodash";
import MarkdownEditor from "@/components/Article/MarkdownEditor.vue";
import { ArrowLeft, ArrowRight } from "@element-plus/icons-vue";

export default {
  name: "ManageView",
  components: { MarkdownEditor, ArrowLeft, ArrowRight },
  data() {
    return {
      searchKeyword: "",
      articleList: [],
      pageNum: 1,
      pageSize: 20,
      isLoading: false,
      hasMore: true,
      totalArticles: 0,
      currentEditingArticle: null,
      sidebarWidth: 320,
      isDragging: false,
      minSidebarWidth: 200,
      maxSidebarWidth: window.innerWidth * 0.8,
      isCollapsed: false,
      isMobile: false, // 判断是否为移动端
      showList: true, // 控制移动端显示列表还是编辑区

      // 批量选择相关
      selectedArticleIds: [], // 选中的文章ID集合
      isAllSelected: false, // 是否全选
      isBatchDeleting: false, // 批量删除状态控制

      form: {
        id: null,
        title: "",
        coverUrl: "",
        status: "DRAFT",
        categoryId: null,
        summary: "",
        content: "",
      },

      rules: {
        title: [
          { required: true, message: "请输入文章标题", trigger: "blur" },
          { max: 200, message: "标题长度不能超过200个字符", trigger: "blur" },
        ],
        content: [{ required: true, message: "请输入文章正文", trigger: "change" }],
        status: [{ required: true, message: "请选择文章状态", trigger: "change" }],
      },
    };
  },

  created() {
    this.loadArticles();
    this.initDragEvents();
    this.checkIsMobile();
    window.addEventListener('resize', this.checkIsMobile);
  },

  beforeUnmount() {
    this.removeDragEvents();
    window.removeEventListener('resize', this.checkIsMobile);
  },

  methods: {
    // 检查是否为移动端
    checkIsMobile() {
      this.isMobile = window.innerWidth < 768;
      // 在移动端默认展开列表
      if (this.isMobile) {
        this.isCollapsed = false;
      }
    },

    // 处理创建文章
    handleCreateArticle() {
      this.createNewArticle();
      // 移动端切换到编辑视图
      if (this.isMobile) {
        this.showList = false;
      }
    },

    // 切换侧边栏折叠/展开状态
    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed;
    },

    // 状态格式化
    formatStatus(status) {
      const map = { DRAFT: "草稿", PUBLISHED: "已发布", DISABLED: "已下架" };
      return map[status] || status;
    },

    getStatusTagType(status) {
      const map = { DRAFT: "info", PUBLISHED: "success", DISABLED: "warning" };
      return map[status] || "default";
    },

    formatDate(dateString) {
      if (!dateString) return "";
      const d = new Date(dateString);
      return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, "0")}-${d
          .getDate()
          .toString()
          .padStart(2, "0")}`;
    },

    truncateTitle(title, max) {
      return title.length > max ? title.slice(0, max - 1) + "…" : title;
    },

    // 拖动相关
    initDragEvents() {
      document.addEventListener("mousemove", this.onDrag);
      document.addEventListener("mouseup", this.stopDrag);
    },
    removeDragEvents() {
      document.removeEventListener("mousemove", this.onDrag);
      document.removeEventListener("mouseup", this.stopDrag);
    },
    startDrag(e) {
      // 移动端不允许拖动
      if (this.isMobile) return;

      this.isDragging = true;
      document.body.style.cursor = "col-resize";
      e.preventDefault();
    },
    onDrag(e) {
      if (!this.isDragging || this.isMobile) return;

      const container = document.querySelector(".split-layout");
      if (!container) return;
      const rect = container.getBoundingClientRect();
      let w = e.clientX - rect.left;
      w = Math.max(this.minSidebarWidth, Math.min(this.maxSidebarWidth, w));
      this.sidebarWidth = w;
    },
    stopDrag() {
      this.isDragging = false;
      document.body.style.cursor = "";
    },

    getUploadHeaders() {
      const headers = {};
      const token = localStorage.getItem("token");
      if (token) headers.Authorization = `Bearer ${token}`;
      return headers;
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

    // 懒加载核心逻辑
    async loadArticles() {
      if (this.isLoading || !this.hasMore) return;
      this.isLoading = true;
      try {
        const params = { page: this.pageNum - 1, size: this.pageSize };
        const url = this.searchKeyword.trim() ? "/api/articles/search" : "/api/articles";
        if (this.searchKeyword.trim()) params.keyword = this.searchKeyword;

        const res = await axios.get(url, {
          params,
          headers: this.getUploadHeaders() // 加载列表也携带Token
        });
        if (res.data.code === 200) {
          const newArticles = res.data.data.content || [];
          this.articleList = [...this.articleList, ...newArticles];
          this.totalArticles = res.data.data.totalElements || res.data.data.total || 0;
          this.hasMore = newArticles.length === this.pageSize;
          this.pageNum++;

          // 重新计算全选状态
          this.handleSingleSelect();
        } else {
          this.$message.error("加载文章失败: " + res.data.message);
        }
      } catch (err) {
        const errorMsg = err.response
            ? `状态码: ${err.response.status}, 信息: ${err.response.data?.message || '未知错误'}`
            : err.message;
        this.$message.error("加载文章请求失败: " + errorMsg);
      } finally {
        this.isLoading = false;
      }
    },

    handleSearch() {
      this.pageNum = 1;
      this.articleList = [];
      this.hasMore = true;
      // 重置选择状态
      this.selectedArticleIds = [];
      this.isAllSelected = false;
      this.loadArticles();
    },

    async handleSelectArticle(row, event) {
      // 如果点击的是复选框，则不触发文章选择
      if (event && event.target.closest('.el-checkbox')) {
        return;
      }

      try {
        const res = await axios.get(`/api/articles/${row.id}`, {
          headers: this.getUploadHeaders()
        });
        if (res.data.code === 200) {
          this.currentEditingArticle = res.data.data;
          this.form = { ...res.data.data };

          // 移动端切换到编辑视图
          if (this.isMobile) {
            this.showList = false;
          }
        } else {
          this.$message.error("获取文章详情失败: " + res.data.message);
        }
      } catch (err) {
        const errorMsg = err.response
            ? `状态码: ${err.response.status}, 信息: ${err.response.data?.message || '未知错误'}`
            : err.message;
        this.$message.error("获取文章详情请求失败: " + errorMsg);
      }
    },

    createNewArticle() {
      this.currentEditingArticle = { id: null };
      this.form = {
        id: null,
        title: "",
        coverUrl: "",
        status: "DRAFT",
        categoryId: null,
        summary: "",
        content: "",
      };
    },

    // 单个删除
    async handleDelete(id) {
      if (!id) {
        this.$message.error("文章ID无效");
        return;
      }

      this.$confirm("确定要删除这篇文章吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        closeOnClickModal: false,
      })
          .then(async () => {
            try {
              const res = await axios.delete(`/api/articles/${id}`, {
                headers: this.getUploadHeaders()
              });

              if (res.data.code === 200) {
                this.$message.success("删除成功");
                // 从选中列表中移除
                this.selectedArticleIds = this.selectedArticleIds.filter(item => item !== id);
                // 重新加载列表
                this.reloadArticleList();
                // 处理当前编辑的文章
                if (this.currentEditingArticle?.id === id) {
                  this.currentEditingArticle = null;
                  if (this.isMobile) this.showList = true;
                }
              } else {
                this.$message.error(`删除失败：${res.data.message || '未知错误'}`);
              }
            } catch (err) {
              const errorMsg = err.response
                  ? `状态码: ${err.response.status}, 信息: ${err.response.data?.message || JSON.stringify(err.response.data)}`
                  : err.message;
              this.$message.error(`删除请求失败：${errorMsg}`);
            }
          })
          .catch(() => this.$message.info("已取消删除"));
    },

    async submitForm() {
      this.$refs.articleForm.validate(async (valid) => {
        if (!valid) return;
        try {
          let res;
          if (this.form.id) {
            res = await axios.put(`/api/articles/${this.form.id}`, this.form, {
              headers: this.getUploadHeaders()
            });
          } else {
            res = await axios.post("/api/articles", this.form, {
              headers: this.getUploadHeaders()
            });
          }

          if (res.data.code === 200) {
            this.$message.success(this.form.id ? "更新成功" : "创建成功");
            this.reloadArticleList();
            this.selectedArticleIds = [];
            this.isAllSelected = false;

            // 移动端保存后返回列表
            if (this.isMobile) {
              this.showList = true;
            }
          } else {
            this.$message.error("保存失败: " + res.data.message);
          }
        } catch (err) {
          const errorMsg = err.response
              ? `状态码: ${err.response.status}, 信息: ${err.response.data?.message || '未知错误'}`
              : err.message;
          this.$message.error("保存请求失败: " + errorMsg);
        }
      });
    },

    // 滚动检测
    handleScroll: _.throttle(function (e) {
      const container = e.target;
      const cards = container.querySelectorAll(".article-card");
      if (this.isLoading || !this.hasMore || cards.length < 3) return;

      const thirdLast = cards[cards.length - 3];
      if (!thirdLast) return;

      const rect = thirdLast.getBoundingClientRect();
      const containerRect = container.getBoundingClientRect();

      const isVisible =
          rect.top < containerRect.bottom && rect.bottom > containerRect.top;

      if (isVisible) {
        this.loadArticles();
      }
    }, 500),

    // 全选/取消全选
    handleSelectAll(val) {
      if (val) {
        // 全选：收集所有文章ID
        this.selectedArticleIds = this.articleList.map(item => item.id);
      } else {
        // 取消全选：清空选中ID
        this.selectedArticleIds = [];
      }
    },

    // 单个选择时更新全选状态
    handleSingleSelect() {
      // 当选中数量等于总数量时，自动勾选全选框
      this.isAllSelected = this.selectedArticleIds.length === this.articleList.length && this.articleList.length > 0;
    },

    // 批量删除（循环调用单个删除接口）
    async handleBatchDelete() {
      // 验证选中的ID
      if (!this.selectedArticleIds || this.selectedArticleIds.length === 0) {
        this.$message.warning("请先选择要删除的文章");
        return;
      }

      const total = this.selectedArticleIds.length;
      this.$confirm(`确定要删除选中的 ${total} 篇文章吗?`, "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        closeOnClickModal: false,
      })
          .then(async () => {
            // 禁用按钮防止重复操作
            this.isBatchDeleting = true;
            let successCount = 0;
            const failIds = [];

            try {
              // 循环调用单个删除接口（顺序执行）
              for (const id of this.selectedArticleIds) {
                try {
                  await axios.delete(`/api/articles/${id}`, {
                    headers: this.getUploadHeaders()
                  });
                  successCount++; // 记录成功数量
                } catch (err) {
                  failIds.push(id); // 记录失败的ID
                  console.error(`删除ID为${id}的文章失败:`, err);
                }
              }

              // 汇总结果提示
              if (successCount > 0) {
                this.$message.success(`成功删除 ${successCount} 篇文章`);
              }
              if (failIds.length > 0) {
                this.$message.error(`有 ${failIds.length} 篇文章删除失败，ID: ${failIds.join(',')}`);
              }

              // 刷新列表并重置选中状态
              this.reloadArticleList();
              this.selectedArticleIds = [];
              this.isAllSelected = false;

              // 处理当前编辑的文章（如果被删除）
              if (this.currentEditingArticle && this.selectedArticleIds.includes(this.currentEditingArticle.id)) {
                this.currentEditingArticle = null;
                if (this.isMobile) this.showList = true;
              }
            } finally {
              // 恢复按钮状态
              this.isBatchDeleting = false;
            }
          })
          .catch(() => {
            this.$message.info("已取消批量删除");
          });
    },

    // 重新加载文章列表的通用方法
    reloadArticleList() {
      this.pageNum = 1;
      this.articleList = [];
      this.hasMore = true;
      this.loadArticles();
    },
  },
};
</script>

<style>
/* 全局盒模型设置 */
::v-deep * {
  box-sizing: border-box;
}

::v-deep html,
::v-deep body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.manage-container {
  width: 100%;
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.split-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
  height: 100%;
  position: relative;
}

.sidebar {
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  height: 95vh;
  overflow: hidden;
  transition: width 0.3ms ease;
  border-right: 1px solid #eee;
  padding-top: 25px;
  position: relative;
  overflow-y: auto;
  z-index: 10;
}

/* 移动端隐藏类 */
.mobile-hidden {
  display: none !important;
}

/* 移动端返回按钮 */
.mobile-back-btn {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 5px;
  background: white;
  padding: 5px 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  display: none;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.el-input {
  flex: 1;
  max-width: 320px;
}

.create-btn {
  padding: 6px 16px;
}

.list-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list-title {
  font-size: 18px;
  font-weight: 600;
}

.list-count {
  font-size: 14px;
  color: #666;
}

.search-box {
  margin-top: 0;
  padding: 10px;
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 8px;
}

.create-btn {
  flex-shrink: 0;
}

.article-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #fafafa;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.list-title {
  margin: 0;
  color: #1f2329;
  font-size: 16px;
  font-weight: 600;
}

.list-count {
  font-size: 12px;
  color: #86909c;
  background-color: #f2f3f5;
  padding: 2px 8px;
  border-radius: 12px;
}

.articles-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.article-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  margin: 0;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.article-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background-color: transparent;
  transition: background-color 0.25s ease;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.article-card.active {
  border-color: #409eff;
  background-color: #f0f7ff;
}

.article-card.active::before {
  background-color: #409eff;
}

.article-cover {
  width: 56px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  margin-right: 12px;
}

.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.article-card:hover .cover-img {
  transform: scale(1.05);
}

.article-info {
  flex: 1;
  min-width: 0;
  margin-right: 8px;
}

.article-title {
  display: block;
  font-size: 14px;
  color: #1d2129;
  font-weight: 500;
  line-height: 1.4;
  margin-bottom: 4px;
  transition: color 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-card:hover .article-title {
  color: #409eff;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  padding: 0 6px;
  height: 18px;
  line-height: 18px;
}

.article-date {
  font-size: 12px;
  color: #86909c;
  white-space: nowrap;
}

.article-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
}

.article-card:hover .article-actions {
  opacity: 1 !important;
}

::v-deep(.article-actions .el-button) {
  padding: 0 6px !important;
  width: 28px !important;
  height: 28px !important;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
}

::v-deep(.article-actions .el-button .el-icon) {
  font-size: 16px !important;
}

::v-deep(.article-actions .delete-btn) {
  color: #ff0000 !important;
}

::v-deep(.article-actions .delete-btn:hover) {
  background-color: #fb7260 !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #86909c;
  background-color: #fff;
  border-radius: 8px;
  margin-top: 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #c9cdd4;
}

.empty-text {
  margin-bottom: 16px;
  font-size: 14px;
}

.divider {
  width: 6px;
  background: rgba(255, 255, 255, 0);
  cursor: col-resize;
  transition: background 0s, left 0s ease;
  user-select: none;
  z-index: 20;
  position: absolute;
  top: 0;
}

.divider:hover {
  background: #e0e0e0;
}

.load-more {
  text-align: center;
  padding: 16px;
  color: #666;
  font-size: 14px;
}

.editor-area {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  background: #dfdfdf;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  transition: left 0s ease;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #86909c;
  font-size: 16px;
  background-color: #fafafa;
}

.editor-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
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

::v-deep .el-form-item__content {
  margin-left: 100px !important;
}

::v-deep .el-form-item__label {
  width: 100px !important;
}

.Main{
  max-height: calc(100vh - 60px);
  width: 100%;
  overflow: hidden;
}

.sidebar::-webkit-scrollbar {
  width: 6px;
}
.sidebar::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 3px;
}
.sidebar::-webkit-scrollbar-track {
  background-color: transparent;
}

.article-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background-color: #f5f7fa;
  padding: 10px 16px;
  border-radius: 6px;
}

/* 批量选择相关样式 */
.list-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.all-select-checkbox {
  transform: scale(0.9);
}

.batch-delete-btn {
  padding: 4px 12px;
  background-color: #f56c6c;
  border-color: #f56c6c;
  transition: all 0.2s;
}

.batch-delete-btn:hover {
  background-color: #e64340 !important;
  border-color: #e64340 !important;
}

.article-checkbox {
  margin-right: 10px;
  flex-shrink: 0;
  transform: scale(0.9);
}

.search-and-create {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-btn {
  position: absolute;
  width: 15px;
  height: 40px;
  background-color: #fff;
  border: 1px solid #000000;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  transition: left 0s ease;
}

.toggle-btn i {
  font-size: 18px;
  color: #000000;
}

.toggle-btn:hover {
  background-color: #f5f5f5;
}

.toggle-btn:hover i {
  color: #ffffff;
}

/* 移动端样式 */
@media (max-width: 767px) {
  .articles-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }

  .article-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 10px;
    height: 100%;
  }

  .article-checkbox {
    margin-right: 8px;
    align-self: flex-start;
  }

  .article-cover {
    width: 100%;
    height: 100px;
    margin-right: 0;
    margin-bottom: 10px;
  }

  .article-info {
    width: 100%;
    margin-right: 0;
  }

  .article-title {
    white-space: normal;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .article-actions {
    margin-top: 10px;
    width: 100%;
    justify-content: flex-end;
    opacity: 1;
  }

  .editor-container {
    padding: 40px 15px 15px;
  }

  /* 移动端表单样式 - 汉堡式布局 */
  .form-item-mobile {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
  }

  ::v-deep .form-item-mobile .el-form-item__label {
    width: 100% !important;
    margin-bottom: 10px;
    text-align: center !important;
    font-weight: bold;
    font-size: 16px;
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 6px 6px 0 0;
    border-bottom: 1px solid #e4e7ed;
  }

  ::v-deep .form-item-mobile .el-form-item__content {
    margin-left: 0 !important;
    border: 1px solid #e4e7ed;
    border-radius: 0 0 6px 6px;
    padding: 10px;
    background-color: white;
  }

  /* 移动端输入框样式 */
  ::v-deep .form-item-mobile .el-input,
  ::v-deep .form-item-mobile .el-select,
  ::v-deep .form-item-mobile .el-textarea {
    width: 100% !important;
    max-width: 100% !important;
  }

  /* Markdown编辑器移动端样式 */
  ::v-deep .form-item-mobile.markdown-editor-item .el-form-item__content {
    padding: 0;
  }

  ::v-deep .form-item-mobile.markdown-editor-item .el-form-item__content > div {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 300px;
  }

  /* 确保Markdown编辑器内容自适应 */
  ::v-deep .markdown-editor {
    width: 100% !important;
  }

  ::v-deep .markdown-editor textarea,
  ::v-deep .markdown-editor .preview {
    width: 100% !important;
    box-sizing: border-box !important;
    overflow: auto !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
  }

  /* 封面图移动端样式 */
  .cover-preview,
  .upload-placeholder {
    width: 100% !important;
    height: auto !important;
    min-height: 150px;
  }

  .mobile-back-btn {
    display: flex;
  }

  .sidebar {
    width: 100% !important;
    height: 100vh !important;
    padding-top: 15px;
  }

  .editor-area {
    width: 100% !important;
    left: 0 !important;
  }

  .search-and-create {
    flex-direction: column;
    align-items: stretch;
  }

  .el-input {
    max-width: 100%;
    width: 100%;
  }

  .create-btn {
    width: 100%;
  }

  .form-header {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 30px;
  }

  .form-header h2 {
    margin: 0;
    text-align: center;
    width: 100%;
  }

  .form-header .el-button {
    width: 100%;
  }

  /* 移动端批量操作样式 */
  .article-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .list-header-right {
    width: 100%;
    justify-content: space-between;
  }

  .batch-delete-btn {
    width: auto;
    font-size: 12px;
    padding: 2px 8px;
  }
}
</style>