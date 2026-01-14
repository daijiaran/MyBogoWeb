<template>
  <div class="profile-edit-container">


    <h2 class="page-title">编辑个人资料</h2>

    <el-card class="profile-card">
      <el-form
          ref="profileFormRef"
          :model="profileForm"
          label-width="120px"
          class="profile-form"
      >
        <!-- 头像上传 -->
        <el-form-item label="头像">
          <div class="avatar-uploader">
            <el-upload
                class="avatar-upload"
                action="/api/upload/image"
                :show-file-list="false"
                :on-success="handleAvatarSuccess"
                :on-error="handleAvatarError"
                :before-upload="beforeAvatarUpload"
                :headers="{ 'Authorization': `Bearer ${(userStore.token || '').trim()}` }"
            >
              <img
                  v-if="profileForm.avatarUrl"
                  :src="$img(profileForm.avatarUrl)"
                  class="avatar"
              />
              <el-icon v-else class="avatar-placeholder">
                <User />
              </el-icon>
            </el-upload>
            <p class="avatar-hint">支持 JPG、PNG、GIF，最大 10MB</p>
          </div>
        </el-form-item>

        <!-- 用户名 -->
        <el-form-item
            label="用户名"
            prop="username"
            :rules="[
            { required: true, message: '请输入用户名', trigger: 'blur' },
            { min: 3, max: 20, message: '3~20个字符', trigger: 'blur' }
          ]"
        >
          <el-input v-model="profileForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <!-- 邮箱（禁用） -->
        <el-form-item label="邮箱">
          <el-input v-model="profileForm.email" disabled />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitProfile">保存资料</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 修改密码 -->
    <el-card class="password-card">
      <h3 class="section-title">修改密码</h3>

      <el-form ref="passwordFormRef" :model="passwordForm" label-width="120px">
        <el-form-item
            label="旧密码"
            prop="oldPassword"
            :rules="[{ required: true, message: '请输入旧密码', trigger: 'blur' }]"
        >
          <el-input type="password" v-model="passwordForm.oldPassword" />
        </el-form-item>

        <el-form-item
            label="新密码"
            prop="newPassword"
            :rules="[{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '至少6位', trigger: 'blur' }]"
        >
          <el-input type="password" v-model="passwordForm.newPassword" />
        </el-form-item>

        <el-form-item
            label="确认密码"
            prop="confirmPassword"
            :rules="[
            { required: true, message: '请输入确认密码', trigger: 'blur' },
            { validator: validateConfirmPassword, trigger: 'blur' }
          ]"
        >
          <el-input type="password" v-model="passwordForm.confirmPassword" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitPassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
  <!-- 移动端引导 -->
  <div class="mobile-guide" v-if="isMobile">
    <el-alert
        title="提示：您正在使用移动设备"
        type="info"
        description="可点击头像上传、更改用户名和密码，向下滑动查看更多功能。"
        show-icon
        :closable="false"
    />
  </div>
</template>


<script setup>
import { ref, reactive, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { User } from "@element-plus/icons-vue";
import { useUserStore } from "@/api/user";
import userApi from "@/api/user";

const userStore = useUserStore();
const router = useRouter();

// 是否为移动端
const isMobile = computed(() => window.innerWidth < 768);

// 表单数据
const profileForm = reactive({
  id: "",
  username: "",
  email: "",
  avatarUrl: ""
});

const passwordForm = reactive({
  oldPassword: "",
  newPassword: "",
  confirmPassword: ""
});

const profileFormRef = ref(null);
const passwordFormRef = ref(null);

onMounted(() => {
  if (!userStore.isLogin) {
    router.push("/login");
    ElMessage.warning("请先登录");
    return;
  }

  profileForm.id = userStore.userId;
  profileForm.username = userStore.username;
  profileForm.email = userStore.email || "未绑定邮箱";
  profileForm.avatarUrl = userStore.avatarUrl || "";
});

// 上传前验证
const beforeAvatarUpload = (file) => {
  const isValidType =
      file.type === "image/jpeg" ||
      file.type === "image/png" ||
      file.type === "image/gif";
  const isLt10M = file.size / 1024 / 1024 < 10;

  if (!isValidType) ElMessage.error("只能上传 JPG/PNG/GIF 格式");
  if (!isLt10M) ElMessage.error("图片大小不能超过 10MB");

  return isValidType && isLt10M;
};

// 上传成功
const handleAvatarSuccess = (response) => {
  if (response.code === 200) {
    const base = (import.meta.env?.VITE_STATIC_BASE_URL || "").trim();
    const fullUrl = `${base.replace(/\/$/, "")}/${response.data.url.replace(/^\//, "")}`;
    profileForm.avatarUrl = fullUrl;
    ElMessage.success("头像上传成功");
  } else {
    ElMessage.error("上传失败：" + response.message);
  }
};

// 上传失败
const handleAvatarError = () => {
  ElMessage.error("头像上传失败，请稍后重试");
};

// 密码二次验证
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error("两次输入不一致"));
  } else {
    callback();
  }
};

// 更新资料
const submitProfile = async () => {
  try {
    await profileFormRef.value.validate();

    const updateData = {
      name: profileForm.username,
      avatarUrl: profileForm.avatarUrl
    };

    const res = await userApi.updateProfile(updateData);

    if (res.data.code === 200) {
      ElMessage.success("资料更新成功");
      userStore.username = profileForm.username;
      userStore.avatarUrl = profileForm.avatarUrl;
    } else {
      ElMessage.error("更新失败：" + res.data.message);
    }
  } catch (e) {
    ElMessage.error("提交失败");
  }
};

// 修改密码
const submitPassword = async () => {
  try {
    await passwordFormRef.value.validate();

    const res = await userApi.changePassword({
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    });

    if (res.data.code === 200) {
      ElMessage.success("密码修改成功，请重新登录");
      await userApi.logout();
      userStore.resetState();
      router.push("/login");
    } else {
      ElMessage.error("修改失败：" + res.data.message);
    }
  } catch (e) {
    ElMessage.error("提交失败");
  }
};
</script>


<style>
/* 1. 全局根元素深色背景（解决最外层白色） */
html, body {
  margin: 0;
  padding: 0;
  background-color: #0a0a0a; /* 最深层背景 */
  min-height: 100vh;
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-weight: 300;
  letter-spacing: 0.3px;
}

/* 2. 深度覆盖Element组件默认白色背景（权重拉满） */
/* 卡片组件 */
::v-deep .el-card {
  background-color: #0a0a0a !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

/* 表单容器 */
::v-deep .el-form {
  background-color: transparent !important; /* 继承卡片背景 */
}

/* 输入框聚焦/hover状态 */
::v-deep .el-input__wrapper:focus-within,
::v-deep .el-input__wrapper:hover {
  box-shadow: 0 0 0 1px rgba(79, 195, 247, 0.3) !important;
  border-color: rgba(79, 195, 247, 0.5) !important;
}

/* 金属风格按钮 */
::v-deep .el-button--primary {
  background: transparent !important;
  border: 1px solid rgba(79, 195, 247, 0.5) !important;
  color: rgba(79, 195, 247, 0.9) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.3s ease !important;
  border-radius: 0 !important;
}

::v-deep .el-button--primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(79, 195, 247, 0.3), transparent);
  transition: left 0.5s;
}

::v-deep .el-button--primary:hover::before {
  left: 100%;
}

::v-deep .el-button--primary:hover {
  border-color: rgba(79, 195, 247, 0.8) !important;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.3) !important;
}

/* 3. 移动端适配补充 */
@media (max-width: 768px) {
  .profile-edit-container {
    padding: 15px;
  }
}

.profile-edit-container {
  /* 移除原有的 background-color 设置，改为继承父元素 */
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: rgba(255, 255, 255, 0.9);
  width: 100%; /* 占满父容器宽度 */
  min-height: 100%; /* 占满父容器高度 */
  background-color: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

:root {
  /* Element Plus border 系列变量全部改深色 */
  --el-border-color-light: rgba(255, 255, 255, 0.1) !important;
  --el-border-color-lighter: rgba(255, 255, 255, 0.05) !important;
  --el-card-border-color: rgba(255, 255, 255, 0.1) !important;

  /* 卡片背景 */
  --el-fill-color-blank: #0a0a0a !important;
  --el-card-bg-color: #0a0a0a !important;

  /* 你的主题变量 */
  --bg-dark: #0a0a0a;
  --card-dark: #0a0a0a;
  --text-light: rgba(255, 255, 255, 0.9);
  --border-dark: rgba(255, 255, 255, 0.1);
  --input-dark: rgba(20, 20, 20, 0.5);
}


/* 2. 容器背景（确保内容区无白色） */
.profile-edit-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: rgba(255, 255, 255, 0.9);
  background-color: #0a0a0a; /* 继承根背景 */
  min-height: 100vh; /* 避免内容过短时背景断层 */
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-weight: 300;
  letter-spacing: 0.3px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.page-title {
  text-align: center;
  font-size: 24px;
  margin-bottom: 20px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 15px;
}

/* 3. 移动端引导提示框（覆盖默认白色） */
.mobile-guide {
  margin-bottom: 16px;
}
::v-deep .el-alert--info {
  background-color: rgba(20, 20, 20, 0.8); /* 深色提示框背景 */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0;
}
::v-deep .el-alert__title,
::v-deep .el-alert__description {
  color: rgba(255, 255, 255, 0.9); /* 提示文字颜色 */
  font-weight: 300;
  letter-spacing: 0.3px;
}

/* 4. 卡片组件（覆盖Element默认白色背景） */
.profile-card,
.password-card {
  background-color: #0a0a0a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0;
  padding: 20px;
  margin-top: 20px;
  box-shadow: none;
}
/* 强制覆盖Element卡片默认样式 */
::v-deep .el-card {
  background-color: #0a0a0a !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0 !important;
}

.section-title {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 15px;
  font-size: 18px;
  font-weight: 300;
  letter-spacing: 1px;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 10px;
}

/* 5. 头像上传区域 */
.avatar-uploader {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.avatar-upload {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: rgba(20, 20, 20, 0.5);
}

.avatar-upload:hover {
  border-color: rgba(79, 195, 247, 0.5);
  box-shadow: 0 0 10px rgba(79, 195, 247, 0.2);
}

.avatar,
.avatar-placeholder {
  width: 160px;
  height: 160px;
  object-fit: cover;
  border-radius: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(20, 20, 20, 0.8);
  color: rgba(255, 255, 255, 0.5);
  font-size: 30px;
}

.avatar-hint {
  margin-top: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 300;
  letter-spacing: 0.3px;
}

/* 6. 表单组件样式覆盖 */
/* 表单标签颜色 */
::v-deep .el-form-item__label {
  color: rgba(255, 255, 255, 0.7) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  font-size: 0.85rem !important;
}

/* 输入框样式 */
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

.el-input__inner{
  color: rgba(255, 255, 255, 0.9) !important;
  font-weight: 300 !important;
}

/* 禁用状态输入框 */
::v-deep .el-input.is-disabled .el-input__inner {
  background-color: rgba(10, 10, 10, 0.5) !important;
  color: rgba(255, 255, 255, 0.5) !important;
  font-weight: 300 !important;
}

/* 7. 按钮样式优化 */
::v-deep .el-button--primary {
  background: transparent !important;
  border: 1px solid rgba(79, 195, 247, 0.5) !important;
  color: rgba(79, 195, 247, 0.9) !important;
  font-weight: 300 !important;
  letter-spacing: 0.5px !important;
  text-transform: uppercase !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.3s ease !important;
  border-radius: 0 !important;
}

::v-deep .el-button--primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(79, 195, 247, 0.3), transparent);
  transition: left 0.5s;
}

::v-deep .el-button--primary:hover::before {
  left: 100%;
}

::v-deep .el-button--primary:hover {
  border-color: rgba(79, 195, 247, 0.8) !important;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.3) !important;
}

/* 8. 移动端适配 */
@media (max-width: 768px) {
  .avatar,
  .avatar-placeholder {
    width: 120px;
    height: 120px;
  }
  ::v-deep .el-form-item__label {
    width: 80px !important;
    font-size: 14px;
  }
  .profile-edit-container {
    padding: 10px;
  }
  .profile-card,
  .password-card {
    padding: 15px;
    margin-top: 15px;
  }
  .page-title {
    font-size: 20px;
  }
}


@media (max-width: 480px) {
  .avatar,
  .avatar-placeholder {
    width: 100px;
    height: 100px;
  }
}
/* 修复个人资料编辑页面的背景问题 */
.Personal-Profile {
  padding: 0 !important; /* 确保无内边距 */
  background-color: #1e1e1e !important;
}

.Personal-Profile .profile-edit-container {
  padding: 20px;
  min-height: 100vh;
  background-color: #1e1e1e;
  width: 100%;
  box-sizing: border-box;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .Personal-Profile .profile-edit-container {
    padding: 10px;
  }
}

</style>