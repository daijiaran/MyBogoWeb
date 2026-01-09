<template>
  <div
      class="sidebar"
      :style="{ width: sidebarWidth + 'px' }"
      @scroll="handleScroll"
  >
    <div class="search-box">
      <el-input
          v-model="searchKeyword"
          placeholder="搜索文章"
          clearable
          size="small"
          @keyup.enter="handleSearch"
      />
      <el-button
          class="create-btn"
          type="primary"
          icon="el-icon-plus"
          size="small"
          @click="$emit('create')"
      >
        新建文章
      </el-button>
    </div>

    <div class="article-list">
      <div class="list-header">
        <h3 class="list-title">文章列表</h3>
        <span class="list-count">{{ articleList.length }} 篇文章</span>
      </div>

      <div
          v-for="item in articleList"
          :key="item.id"
          class="article-card"
          :class="{ active: currentArticle?.id === item.id }"
          @click="$emit('select', item)"
      >
        <div class="article-info">
          <span>{{ item.title }}</span>
        </div>
        <el-button
            type="text"
            icon="el-icon-delete"
            @click.stop="handleDelete(item.id)"
        ></el-button>
      </div>

      <div class="load-more">
        <el-loading v-if="isLoading" text="加载中..." />
        <p v-else-if="!hasMore">已加载全部文章</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ArticleList',
  props: {
    sidebarWidth: Number,
    currentArticle: Object,
  },
  data() {
    return {
      searchKeyword: '',
      articleList: [],
      pageNum: 1,
      pageSize: 50,
      hasMore: true,
      isLoading: false,
    }
  },
  created() {
    this.loadArticles()
  },
  methods: {
    async loadArticles() {
      if (this.isLoading || !this.hasMore) return
      this.isLoading = true
      const params = { page: this.pageNum - 1, size: this.pageSize }
      if (this.searchKeyword) params.keyword = this.searchKeyword
      const res = await axios.get('/api/articles', { params })
      if (res.data.code === 200) {
        const newArticles = res.data.data.content || []
        this.articleList.push(...newArticles)
        this.hasMore = newArticles.length === this.pageSize
        this.pageNum++
      }
      this.isLoading = false
    },
    handleSearch() {
      this.pageNum = 1
      this.articleList = []
      this.hasMore = true
      this.loadArticles()
    },
    async handleDelete(id) {
      await axios.delete(`/api/articles/${id}`)
      this.articleList = this.articleList.filter((a) => a.id !== id)
      this.$message.success('删除成功')
    },
    handleScroll(e) {
      const container = e.target
      if (container.scrollTop + container.clientHeight >= container.scrollHeight - 100) {
        this.loadArticles()
      }
    },
    reload() {
      this.pageNum = 1
      this.articleList = []
      this.hasMore = true
      this.loadArticles()
    },
  },
}
</script>

<style scoped>
.sidebar {
  background: #f5f5f5;
  border-right: 1px solid #eee;
  overflow-y: auto;
}
.article-card {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #fff;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
}
.article-card.active {
  background: #f0f7ff;
  border-left: 3px solid #409eff;
}
</style>
