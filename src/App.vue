<script setup>
import Navigationbar from "@/components/Navigationbar.vue";
// import UserView from "./views/UserView.vue";
</script>

<template>
  <div class="app-wrapper">
    <!-- 导航栏固定在顶部，动态类：hidden -->
    <Navigationbar></Navigationbar>
    <!-- 内容区域，仅内部滚动，ref绑定 -->
    <div class="other">
      <router-view/>
<!--      <user-view></user-view>-->
    </div>
  </div>
</template>

<style>
.app-wrapper {
  background-color: rgb(255, 255, 255);
  width: 100%;
  min-height: 100vh; /* 占满整个视口高度 */
  position: fixed; /* 固定在视口，不随滚动移动 */
  overflow: hidden; /* 禁止父元素滚动 */
}

/* 导航栏固定在顶部（假设导航栏高度为80px，需与下方other的top值匹配） */
.navbar {
  background: rgba(255, 0, 0, 0);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 80px; /* 明确导航栏高度 */
  z-index: 10; /* 确保在内容上方 */
  transition: transform 0.3s ease-in-out; /* 平滑动画，使用transform避免布局重排 */
}

/* 隐藏状态：向上平移隐藏 */
.navbar.hidden {
  transform: translateY(-100%); /* 完全隐藏，-80px也可，但百分比更灵活 */
}

/* 内容区域：高度由内部元素总高度决定，超出时内部滚动 */
.other {
  background-color: rgba(255, 255, 255, 0);
  width: 100%;
  /* 高度由内部元素总高度决定（自适应内容） */
  height: auto;
  /* 最大高度限制为「视口高度 - 导航栏高度」，避免内容过长时撑满页面 */
  max-height: calc(100vh);
  /* 从导航栏下方开始显示 */
  padding-top: 60px;
  /* 内容超出最大高度时，仅在该区域内部滚动 */
  overflow: auto;
  transition: padding-top 0.3s ease-in-out; /* 可选：同步调整padding以填充空间 */
}

/* 美化滚动条（可选） */
.other::-webkit-scrollbar {
  width: 6px;
}
.other::-webkit-scrollbar-track {
  background: transparent;
}
.other::-webkit-scrollbar-thumb {
  background: rgba(147, 147, 147, 0.61);
  border-radius: 3px;
}
.other::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>