<template>
  <div
    class="card"
    :style="{
      width: width + 'px',
      height: height + 'px',
      'max-width': '100%'
    }"
    @click="handleClick"
  >
    <div class="card-image-wrapper">
      <img
        :src="resolvedImage"
        :alt="title"
        class="card-image"
        :class="{ 'image-loading': !imageLoaded }"
        @load="imageLoaded = true"
        @error="handleImageError"
      >
      <div
        v-if="!imageLoaded"
        class="image-loader"
      />
    </div>

    <div class="card-content">
      <h3 class="card-title">
        {{ title }}
      </h3>
      <p
        v-if="description"
        class="card-description"
      >
        {{ description }}
      </p>
    </div>

    <div class="card-overlay">
      <span class="overlay-text">查看详情</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardList',
  props: {
    imageName: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    width: {
      type: Number,
      default: 400
    },
    height: {
      type: Number,
      default: 300
    },
    link: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      imageLoaded: false
    };
  },
  computed: {
    resolvedImage() {
      return require(`@/assets/MyPicture/${this.imageName}`);
    }
  },
  methods: {
    handleClick() {
      if (this.link) {
        if (this.$router) {
          this.$router.push(this.link);
        } else {
          window.location.href = this.link;
        }
      }
    },
    // 新增图片错误处理方法
    handleImageError(e) {
      console.error('图片加载失败:', this.imageName);
      e.target.alt = '图片加载失败';
    }
  }
};
</script>

<style scoped>
/* 基础卡片样式 */
.card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  transition:
      transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1),
      box-shadow 0.4s ease;
  background: white;
}

/* 悬停动效：上浮+阴影增强 */
.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
}

/* 图片容器（保持宽高比） */
.card-image-wrapper {
  position: relative;
  width: 100%;
  height: 60%;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
  opacity: 1;
}

/* 图片加载动画 */
.image-loader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(120deg, #f5f5f5 30%, #e0e0e0 38%, #e0e0e0 40%, #f5f5f5 48%);
  background-size: 200% 100%;
  animation: loader-wave 1.5s infinite;
}

.image-loading {
  opacity: 0;
  height: 0;
}

@keyframes loader-wave {
  100% { background-position: -200% 0; }
}

/* 内容区域 */
.card-content {
  padding: 20px;
  height: 40%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-title {
  margin: 0 0 10px;
  font-size: 1.4rem;
  font-weight: 600;
  color: #333;
  transition: color 0.3s;
}

.card-description {
  margin: 0;
  color: #666;
  font-size: 0.95rem;
  line-height: 1.5;
}

/* 悬停覆盖层（渐变出现） */
.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
      135deg,
      rgba(106, 17, 203, 0.3) 0%,   /* #6a11cb 透明度70% */
      rgba(37, 117, 252, 0.3) 100%  /* #2575fc 透明度70% */
  );
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.card:hover .card-overlay {
  opacity: 1;
}

.overlay-text {
  color: white;
  font-weight: 600;
  font-size: 1.2rem;
  letter-spacing: 1px;
}
</style>