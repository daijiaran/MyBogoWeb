<template>
  <div class="Main">
    <div class="manage-container">
      <div class="split-layout" ref="splitLayout">
        <!-- 右侧文章列表（移动后） -->
        <div
            class="sidebar"
            :class="{ 'mobile-hidden': isMobile && !showList }"
            :style="{
            width: sidebarWidth + 'px',
            transform: isCollapsed ? `translateX(${sidebarWidth}px)` : 'translateX(0)',
            transition: 'transform 0.3s ease',
            right: 0
          }"
        >

          <div class="article-container">
            <!-- 上方：文章列表标题 + 数量 -->
            <div class="article-header">
              <h3 class="list-title" style="color: #e0e0e0">文章列表</h3>
              <span class="list-count">{{ articleList.length + "/" + totalArticles }} 篇文章</span>
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
                  @click="handleSelectArticle(item)"
                  :data-article-index="articleList.length - index - 1"
              >
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

        <!-- 左侧编辑区：替换为 ReleaseComponent -->
        <div
            class="editor-area"
            :class="{ 'mobile-hidden': isMobile && showList }"
            :style="{
            right: isCollapsed ? '6px' : `${sidebarWidth + 6}px`,
            left: 0
          }"
        >
          <div v-if="!currentEditingArticle && !isMobile" class="placeholder">
            <p>请在右侧选择文章或新建一篇</p>
          </div>

          <!-- 引入自定义发布组件 -->
          <ReleaseComponent
              v-else
              ref="releaseComponentRef"
              :current-article="currentEditingArticle"
              :is-mobile="isMobile"
              :upload-headers="getUploadHeaders()"
              @save-success="handleEditorSave"
              @cancel="handleEditorCancel"
          />
        </div>

        <!-- 分隔线 - 可拖动（调整位置） -->
        <div
            class="divider"
            @mousedown="startDrag"
            :style="{
            right: isCollapsed ? '0' : `${sidebarWidth}px`,
            height: '100%',
            display: isMobile ? 'none' : 'block'
          }"
        ></div>

        <!-- 折叠/展开按钮（调整位置和图标） -->
        <div
            class="toggle-btn"
            @click="toggleSidebar"
            :style="{
            right: isCollapsed ? '6px' : `${sidebarWidth}px`,
            top: '50%',
            transform: 'translateY(-50%)',
            display: isMobile ? 'none' : 'block'
          }"
        >
          <ElIcon v-if="isCollapsed">
            <ArrowLeft />
          </ElIcon>
          <ElIcon v-else>
            <ArrowRight />
          </ElIcon>
        </div>

        <!-- 移动端返回按钮（调整文字） -->
        <div class="mobile-back-btn" @click="showList = true" v-if="isMobile && !showList">
          <ElIcon>
            <ArrowLeft />
          </ElIcon>
          <span>返回列表</span>
        </div>

        <!--右上角固定保存按钮-->
        <div class="mobile-footer-actions" v-if="isMobile && !showList">
          <el-button
              type="primary"
              @click="handleSaveClick"
              class="footer-btn submit-btn"
          >
            保存
          </el-button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import _ from "lodash";
// 引入重命名后的组件
import ReleaseComponent from "@/components/User/ReleaseComponent.vue";
import { ArrowLeft, ArrowRight } from "@element-plus/icons-vue";
// 引入用户API
import userApi from "../../api/user";

export default {
  name: "ReleaseManager",
  computed: {
    ReleaseComponent() {
      return ReleaseComponent
    }
  },
  components: {
    ReleaseComponent, // 注册重命名后的组件
    ArrowLeft,
    ArrowRight
  },
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
      userId: null, // 当前用户ID
    };
  },

  created() {
    // 先获取用户ID，再加载文章
    this.getCurrentUserInfo();
    this.initDragEvents();
    this.checkIsMobile();
    window.addEventListener('resize', this.checkIsMobile);
  },

  beforeUnmount() {
    this.removeDragEvents();
    window.removeEventListener('resize', this.checkIsMobile);
  },

  methods: {

    handleSaveClick() {
      // 确保子组件已经挂载
      if (this.$refs.releaseComponentRef && this.$refs.releaseComponentRef.submitForm) {
        this.$refs.releaseComponentRef.submitForm();
      } else {
        console.error('ReleaseComponent 未挂载或 submitForm 方法不存在');
      }
    },
    // 获取当前用户信息
    async getCurrentUserInfo() {
      try {
        const response = await userApi.getCurrentUser();
        if (response.data.code !== 200) {
          throw new Error(response.data.message || '获取用户信息失败');
        }
        this.userId = response.data.data.id;
        if (!this.userId) {
          throw new Error('用户ID为空，请重新登录');
        }
        this.loadArticles(); // 获取ID后加载文章
      } catch (err) {
        this.$message.error(`用户信息获取失败：${err.message}，请刷新页面或重新登录`);
        console.error("用户信息获取失败：", err);
      }
    },

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

    // 拖动相关（修改拖动逻辑，适配右侧布局）
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
      // 计算右侧侧边栏宽度：容器总宽度 - 鼠标距离左侧的距离
      let w = rect.right - e.clientX;
      w = Math.max(this.minSidebarWidth, Math.min(this.maxSidebarWidth, w));
      this.sidebarWidth = w;
    },
    stopDrag() {
      this.isDragging = false;
      document.body.style.cursor = "";
    },

    // 获取上传请求头（传递给子组件）
    getUploadHeaders() {
      const headers = {};
      const token = localStorage.getItem("token");
      if (token) headers.Authorization = `Bearer ${token}`;
      return headers;
    },

    // 懒加载核心逻辑通过用户UUID
    async loadArticles() {
      // 如果还没获取到用户ID，不加载文章
      if (!this.userId) return;

      if (this.isLoading || !this.hasMore) return;
      this.isLoading = true;
      try {
        // 统一调用后端的 by-PublishUUID 接口
        const url = "/api/articles/filter/by-publisher-uuid"; // 与后端新路径一致
        // 构造参数（仅传递后端需要的 page、size、publisherId）
        const params = {
          page: this.pageNum - 1,
          size: this.pageSize,
          publisherId: this.userId // 发布者ID参数（后端接口需要）
        };

        // 调用接口获取文章列表（后端返回该发布者的所有文章分页数据）
        const res = await axios.get(url, { params });

        if (res.data.code === 200) {
          // 后端返回的原始文章列表
          let newArticles = res.data.data.content || [];

          // 如有搜索关键词，在前端筛选包含关键词的文章
          if (this.searchKeyword.trim()) {
            const keyword = this.searchKeyword.trim().toLowerCase(); // 统一转为小写，忽略大小写
            newArticles = newArticles.filter(article => {
              // 假设文章包含 title（标题）和 content（内容）字段，可根据实际字段调整
              const titleMatch = article.title?.toLowerCase().includes(keyword);
              const contentMatch = article.content?.toLowerCase().includes(keyword);
              // 标题或内容包含关键词即保留
              return titleMatch || contentMatch;
            });
          }

          // 更新文章列表（合并已有列表和新筛选的列表）
          this.articleList = [...this.articleList, ...newArticles];

          // 计算总数量（如果有筛选，显示筛选后的总数；否则用后端返回的总数）
          this.totalArticles = this.searchKeyword.trim()
              ? this.articleList.length // 筛选后的数据总数
              : (res.data.data.totalElements || res.data.data.total || 0); // 后端原始总数

          // 判断是否还有更多数据（基于后端返回的原始分页逻辑，避免因前端筛选导致误判）
          this.hasMore = res.data.data.content?.length === this.pageSize;

          // 页码自增（继续加载下一页）
          this.pageNum++;
        } else {
          this.$message.error("加载文章失败: " + res.data.message);
        }
      } catch (err) {
        this.$message.error("请求失败: " + err.message);
      } finally {
        this.isLoading = false;
      }
    },

    handleSearch() {
      this.pageNum = 1;
      this.articleList = [];
      this.hasMore = true;
      this.loadArticles();
    },

    async handleSelectArticle(row) {
      try {
        const res = await axios.get(`/api/articles/${row.id}`);
        if (res.data.code === 200) {
          const articleData = res.data.data;
          // 确保摘要字段正确映射（兼容可能的字段名差异）
          this.currentEditingArticle = {
            ...articleData,
            summary: articleData.summary || articleData.abstract || articleData.description || ''
          };
          console.log('ReleaseManager 获取到的文章数据：', articleData);
          console.log('ReleaseManager 摘要字段值：', this.currentEditingArticle.summary);

          // 移动端切换到编辑视图
          if (this.isMobile) {
            this.showList = false;
          }
        } else {
          this.$message.error("获取文章详情失败: " + res.data.message);
        }
      } catch (err) {
        this.$message.error("请求失败: " + err.message);
      }
    },

    // 创建新文章（清空当前编辑状态）
    createNewArticle() {
      this.currentEditingArticle = { id: null };
    },

    async handleDelete(id) {
      this.$confirm("确定要删除这篇文章吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        closeOnClickModal: false,
      })
          .then(async () => {
            const res = await axios.delete(`/api/articles/${id}`);
            if (res.data.code === 200) {
              this.$message.success("删除成功");
              this.pageNum = 1;
              this.articleList = [];
              this.hasMore = true;
              this.loadArticles();
              if (this.currentEditingArticle?.id === id) {
                this.currentEditingArticle = null;
                // 移动端删除当前编辑的文章后返回列表
                if (this.isMobile) {
                  this.showList = true;
                }
              }
            } else {
              this.$message.error("删除失败: " + res.data.message);
            }
          })
          .catch(() => this.$message.info("已取消删除"));
    },


    // 子组件保存成功回调（改造成父组件负责提交）
    async handleEditorSave(articleData) {
      try {
        // 1. 校验userId是否有效（关键：避免publisherId为null）
        if (!this.userId) {
          this.$message.error("用户未登录或登录状态失效，请刷新页面重试");
          return;
        }

        // 2. 注入发布者ID + 过滤无效字段（核心修复）
        const submitData = {
          ...articleData,
          publisherId: this.userId, // 注入当前用户ID
          createTime: undefined, // 强制移除创建时间（避免格式错误）
          updateTime: undefined, // 强制移除更新时间（避免格式错误）
          categoryId: articleData.categoryId || undefined // 若为null则不传递（避免后端验证警告）
        };

        // 3. 确认请求类型（新建/编辑）
        const isUpdate = !!submitData.id;
        const url = isUpdate ? `/api/articles/${submitData.id}` : `/api/articles`;
        const method = isUpdate ? 'put' : 'post';

        // 4. 携带认证头提交请求（关键修复：之前遗漏）
        const res = await axios({
          method,
          url,
          data: submitData,
          headers: this.getUploadHeaders() // 包含Token的认证头
        });

        // 5. 提交成功处理
        if (res.data.code === 200) {
          this.$message.success(isUpdate ? "更新成功" : "创建成功");
          // 重置并刷新列表
          this.pageNum = 1;
          this.articleList = [];
          this.hasMore = true;
          this.loadArticles();
          // 移动端返回列表
          if (this.isMobile) {
            this.showList = true;
          }
        } else {
          this.$message.error(`保存失败：${res.data.message || '后端返回未知错误'}`);
        }
      } catch (err) {
        // 6. 精准错误提示（便于排查）
        const errorDetail = err.response
            ? `状态码：${err.response.status}，响应：${JSON.stringify(err.response.data || '无')}`
            : `网络错误：${err.message}`;
        this.$message.error(`提交请求失败：${errorDetail}`);
        console.error("提交失败详情：", err); // 控制台打印完整错误，方便调试
      }
    },

    // 子组件取消编辑回调
    handleEditorCancel() {
      this.currentEditingArticle = null;
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
  background-color: rgba(0, 0, 0, 0);
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
  background: rgb(0, 0, 0);
}

.sidebar {
  background: linear-gradient(to bottom, rgba(30, 30, 30, 0), rgba(20, 20, 20, 0));
  display: flex;
  flex-direction: column;
  height: 95vh;
  overflow: hidden;
  transition: width 0.3ms ease;
  border-left: 1px solid rgba(165, 165, 165, 0.44); /* 改为左边框 */
  padding-top: 25px;
  position: absolute; /* 改为绝对定位 */
  overflow-y: auto;
  z-index: 10;
  border-radius: 40px;
}

/* 侧边栏滚动条样式 */
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: rgb(234, 234, 234);
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgb(100, 100, 100);
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(150, 150, 150, 0);
}

.article-container {
  padding: 0 16px 16px;
  color: #ffffff;
}

.article-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  background: black;
  border-bottom: 1px solid rgba(220, 220, 220, 0);
}

.search-and-create {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 0;
}

/* 移动端隐藏类 */
.mobile-hidden {
  display: none !important;
}

/* 移动端返回按钮 */
.mobile-back-btn {
  position: fixed;
  top: 85px;
  left: 10px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 5px;
  background: #2d2d2d;
  color: #e0e0e0;
  padding: 5px 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  cursor: pointer;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  border-bottom: 1px solid #555;
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
  color: #ffffff;
}

.list-count {
  font-size: 14px;
  color: #000000;
}

.search-box {
  margin-top: 0;
  padding: 10px;
  background: rgba(45, 45, 45, 0.6);
  border-bottom: 1px solid rgba(100, 100, 100, 0.3);
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
  background-color: rgba(20, 20, 20, 0.3);
}

/* 文章列表滚动条样式 */
.article-list::-webkit-scrollbar {
  width: 6px;
}

.article-list::-webkit-scrollbar-track {
  background: rgba(20, 20, 20, 0.5);
}

.article-list::-webkit-scrollbar-thumb {
  background: rgba(100, 100, 100, 0.5);
  border-radius: 3px;
}

.article-list::-webkit-scrollbar-thumb:hover {
  background: rgba(150, 150, 150, 0.7);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(100, 100, 100, 0.3);
}

.list-title {
  margin: 0;
  color: #e0e0e0;
  font-size: 16px;
  font-weight: 600;
}

.list-count {
  font-size: 12px;
  color: #999;
  background-color: rgba(45, 45, 45, 0.6);
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
  background: rgba(45, 45, 45, 0.6);
  border-radius: 8px;
  padding: 12px;
  margin: 0;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.article-card::before {
  content: '';
  position: absolute;
  right: 0; /* 改为右侧边框 */
  top: 0;
  height: 100%;
  width: 3px;
  background-color: transparent;
  transition: background-color 0.25s ease;
}

.article-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  background: rgba(60, 60, 60, 0.8);
}

.article-card.active {
  border-color: #4fc3f7;
  background-color: rgba(79, 195, 247, 0.15);
}

.article-card.active::before {
  background-color: #4fc3f7;
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
  color: #e0e0e0;
  font-weight: 500;
  line-height: 1.4;
  margin-bottom: 4px;
  transition: color 0.2s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.article-card:hover .article-title {
  color: #4fc3f7;
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
  color: #999;
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
  color: #999;
  background-color: rgba(45, 45, 45, 0.6);
  border-radius: 8px;
  margin-top: 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #666;
}

.empty-text {
  margin-bottom: 16px;
  font-size: 14px;
}

/* 分隔线调整到右侧 */
.divider {
  width: 6px;
  background: rgba(100, 100, 100, 0.3);
  cursor: col-resize;
  transition: background 0s, right 0s ease;
  user-select: none;
  z-index: 20;
  position: absolute;
  top: 0;
}

.divider:hover {
  background: rgba(150, 150, 150, 0.6);
}

.load-more {
  text-align: center;
  padding: 16px;
  color: #999;
  font-size: 14px;
}

/* 编辑区调整到左侧 */
.editor-area {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 326px; /* 默认宽度+分隔线宽度 */
  /* 从浅灰透明到深灰透明的垂直渐变，柔和不刺眼 */
  background: linear-gradient(to bottom, rgba(20, 20, 20, 0.8), rgba(15, 15, 15, 0.95));
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  transition: right 0s ease;
  border-radius: 40px;

}

.editor-area::-webkit-scrollbar {
  display: none;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
  background-color: rgba(30, 30, 30, 0.5);
}

/* 保留编辑器容器基础样式，具体编辑样式在 ReleaseComponent 中 */
.toggle-btn {
  position: absolute;
  width: 15px;
  height: 40px;
  background-color: rgba(45, 45, 45, 0.8);
  border: 1px solid #555;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  z-index: 1000;
  transition: right 0s ease;
  color: #e0e0e0;
}

.toggle-btn i {
  font-size: 18px;
  color: #e0e0e0;
}

.toggle-btn:hover {
  background-color: rgba(60, 60, 60, 0.9);
  border-color: #4fc3f7;
}

.toggle-btn:hover i {
  color: #4fc3f7;
}

/* 移动端样式 */
@media (max-width: 767px) {

  .mobile-footer-actions {
    position: fixed;
    top: 85px;       /* 距离顶部15px */
    right: 35px;     /* 距离右边15px */
    z-index: 9999;   /* 确保悬浮在最上层 */
    border-radius: 4px;
    color: #ffffff;
  }

  /* 按钮内部样式可保持原样 */
  .footer-btn.submit-btn {
    background-color: #4fc3f7;
    border-color: #4fc3f7;
    color: #fff;
  }

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
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .article-actions {
    margin-top: 10px;
    width: 100%;
    justify-content: flex-end;
    opacity: 1;
  }

  /* 移动端表单容器样式（配合 ReleaseComponent） */
  .mobile-back-btn {
    display: flex;
  }

  .sidebar {
    width: 100% !important;
    height: 100vh !important;
    padding-top: 15px;
    right: 0 !important;
    border-left: none;
  }

  .editor-area {
    width: 100% !important;
    right: 0 !important;
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

  .divider {
    display: none !important;
  }
}
</style>