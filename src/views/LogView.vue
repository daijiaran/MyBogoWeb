

<script>


import LoadArticlesWithCard_UseCateGory from "@/components/Article/LoadArticlesWithCard_UseCateGory.vue";

export default {
  name: 'LogView',
  components: {
    LoadArticlesWithCard_UseCateGory,
  }
}

</script>

<template>
  <LoadArticlesWithCard_UseCateGory :category-id="3" style="padding-top: 80PX"></LoadArticlesWithCard_UseCateGory>
</template>


<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

/* 网格容器设置 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: clamp(12px, 2vw, 24px);
  padding: 20px clamp(10px, 10vw, 40px);
  place-content: center; /* 新增：让网格内容区域在容器中居中 */
}

/* 卡片基础样式 */
cards {
  display: grid; /* 启用嵌套Grid优化内部布局 */
  grid-template-rows: auto 1fr auto; /* 头部/图片/内容三段式结构 */
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 12px rgba(0,0,0,0.08);
  transition: transform 0.3s ease, box-shadow 0.3s;
  background: white;
}

/* 交互增强 */
cards:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 20px rgba(0,0,0,0.15);
}

/* 图片自适应 */
card-image img {
  width: 100%;
  height: 200px;
  object-fit: cover; /* 保持比例裁剪填充 */
}

/* 响应式适配 */
@media (max-width: 900px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr); /* 中屏双列 */
  }
}
@media (max-width: 600px) {
  .card-grid {
    grid-template-columns: 1fr; /* 小屏单列 */
  }
}
</style>
