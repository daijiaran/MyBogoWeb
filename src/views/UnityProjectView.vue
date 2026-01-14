

<script>


import LoadArticlesWithCard_UseCateGory from "@/components/Article/LoadArticlesWithCard_UseCateGory.vue";

export default {
  name: 'LifeLogView',
  components: {
    LoadArticlesWithCard_UseCateGory,
  }
}

</script>

<template>
  <LoadArticlesWithCard_UseCateGory :category-id="1" style="padding-top: 80PX"></LoadArticlesWithCard_UseCateGory>
</template>


<style>
#app {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #f0f0f0;
  margin-top: 60px;
  background: #0a0a0a;
}

/* 网格容器设置 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1px;
  padding: 20px clamp(10px, 10vw, 40px);
  place-content: center;
  background: rgba(255, 255, 255, 0.05);
}

/* 卡片基础样式 */
cards {
  display: grid;
  grid-template-rows: auto 1fr auto;
  overflow: hidden;
  transition: all 0.3s ease;
  background: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

/* 交互增强 */
cards:hover {
  border-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
}

/* 图片自适应 */
card-image img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

/* 响应式适配 */
@media (max-width: 900px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 600px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
