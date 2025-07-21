<template>
  <div class="profile-edit-container">
    <h2>编辑个人资料</h2>

    <el-card>
      <!-- 基本资料编辑 -->
      <el-form ref="profileFormRef" :model="profileForm" label-width="120px" class="profile-form">
        <!-- 头像上传区域 -->
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
            <img v-if="profileForm.avatarUrl" :src="profileForm.avatarUrl" class="avatar" />
            <el-icon v-else class="avatar-placeholder"><User /></el-icon>
            </el-upload>
            <p class="avatar-hint">点击上传头像，支持 JPG、PNG、GIF 格式，不超过 10MB</p>
          </div>
        </el-form-item>

        <!-- 其他表单内容 -->
        <el-form-item label="用户名" prop="username" :rules="[{ required: true, message: '请输入用户名', trigger: 'blur' }, { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }]">
          <el-input v-model="profileForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="profileForm.email" disabled placeholder="用户邮箱"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitProfile">保存资料</el-button>
          <el-button type="info" @click="submitWithFixedUrl" style="margin-left: 10px;">测试固定URL提交</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 密码修改区域 -->
    <el-card class="password-card">
      <h3>修改密码</h3>
      <el-form ref="passwordFormRef" :model="passwordForm" label-width="120px" class="password-form">
        <el-form-item label="旧密码" prop="oldPassword" :rules="[{ required: true, message: '请输入旧密码', trigger: 'blur' }]">
          <el-input type="password" v-model="passwordForm.oldPassword" placeholder="请输入旧密码"></el-input>
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword" :rules="[{ required: true, message: '请输入新密码', trigger: 'blur' }, { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' }]">
          <el-input type="password" v-model="passwordForm.newPassword" placeholder="请输入新密码"></el-input>
        </el-form-item>

        <el-form-item label="确认新密码" prop="confirmPassword" :rules="[{ required: true, message: '请确认新密码', trigger: 'blur' }, { validator: validateConfirmPassword, trigger: 'blur' }]">
          <el-input type="password" v-model="passwordForm.confirmPassword" placeholder="请确认新密码"></el-input>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitPassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import {ref, onMounted, reactive} from 'vue';
import {useRouter} from 'vue-router';
import {ElMessage} from 'element-plus';
import {User} from '@element-plus/icons-vue';
import {useUserStore} from '@/api/user';
import userApi from '@/api/user';

// 状态与路由
const userStore = useUserStore();
const router = useRouter();

// 表单数据
const profileForm = reactive({
  id: '',
  username: '',
  email: '',
  avatarUrl: ''
});

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 表单引用
const profileFormRef = ref(null);
const passwordFormRef = ref(null);

// 初始化逻辑
onMounted(() => {
  if (!userStore.isLogin) {
    router.push('/login');
    ElMessage.warning('请先登录');
    return;
  }

  // 初始化用户信息（统一使用avatarUrl字段）
  profileForm.id = userStore.userId || '';
  profileForm.username = userStore.username || '';
  profileForm.email = userStore.email || '未绑定邮箱';
  profileForm.avatarUrl = userStore.avatarUrl || '';  // 修正：使用avatarUrl字段

  console.log('初始化后用户信息:', profileForm);
  console.log('上传请求Authorization头:', `Bearer ${(userStore.token || '').trim()}`);
});

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/gif';
  const isLt10M = file.size / 1024 / 1024 < 10;

  if (!isJpgOrPng) ElMessage.error('上传头像图片只能是 JPG、PNG 或 GIF 格式!');
  if (!isLt10M) ElMessage.error('上传头像图片大小不能超过 10MB!');
  return isJpgOrPng && isLt10M;
};

// 头像上传成功处理（使用正确的静态资源BaseUrl）
const handleAvatarSuccess = (response) => {
  console.log('上传接口返回的原始响应:', response);
  if (response.code === 200) {
    // 使用后端服务根路径作为BaseUrl（不含/api前缀）
    const baseUrl = (import.meta.env?.VITE_API_BASE_URL || 'http://localhost:8080').trim();
    const imagePath = response.data?.url?.trim() || '';
    // 处理URL拼接，避免重复斜杠
    const fullUrl = `${baseUrl.replace(/\/$/, '')}/${imagePath.replace(/^\//, '')}`;
    console.log('上传生成的完整URL:', fullUrl);
    profileForm.avatarUrl = fullUrl;
    ElMessage.success('头像上传成功');
  } else {
    ElMessage.error(`头像上传失败：${response.message || '服务器未返回错误信息'}`);
  }
};

// 上传失败回调
const handleAvatarError = (err) => {
  console.error('上传请求错误详情:', err);
  ElMessage.error('头像上传失败：网络异常或服务器错误，请稍后重试');
};

// 确认密码验证
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'));
  } else {
    callback();
  }
};

// 提交资料修改（同步正确的头像字段）
const submitProfile = async () => {
  try {
    console.log('===== 开始提交资料 =====');
    await profileFormRef.value.validate();

    const cleanAvatarUrl = profileForm.avatarUrl
        ?.replace(/\s+/g, '')
        .replace(/\u00A0/g, '')
        .replace(/\u200B/g, '');

    if (cleanAvatarUrl?.startsWith('data:image/')) {
      ElMessage.error('错误：禁止直接提交Base64图片数据，请上传后提交URL');
      return;
    }

    const updateData = {
      name: profileForm.username,
      avatarUrl: cleanAvatarUrl,
    };
    console.log('提交给后端的完整参数:', updateData);

    const response = await userApi.updateProfile(updateData);
    console.log('服务器响应:', response);

    if (response.data?.code === 200) {
      ElMessage.success('资料更新成功');
      userStore.username = profileForm.username;
      userStore.avatarUrl = cleanAvatarUrl;  // 修正：同步到avatarUrl字段
    } else {
      ElMessage.error('资料更新失败：' + (response.data?.message || '未知错误'));
    }
  } catch (error) {
    console.error('提交资料失败:', error);
    ElMessage.error('提交失败：' + (error.response?.data?.message || error.message || '网络异常'));
  }
};

// 临时测试：使用固定URL提交（同步正确的头像字段）
const submitWithFixedUrl = async () => {
  try {
    await profileFormRef.value.validate();
    const fixedUrl = '/test-avatar-no-space.png';
    console.log('===== 测试固定URL提交 =====');
    console.log('使用的固定URL:', fixedUrl);

    const updateData = {
      name: profileForm.username,
      avatarUrl: fixedUrl,
    };

    const response = await userApi.updateProfile(updateData);
    console.log('固定URL提交响应:', response);

    if (response.data?.code === 200) {
      ElMessage.success('固定URL提交成功！');
      userStore.username = profileForm.username;
      userStore.avatarUrl = fixedUrl;  // 修正：同步到avatarUrl字段
    } else {
      ElMessage.error('固定URL仍提交失败：' + (response.data?.message || '未知错误'));
    }
  } catch (error) {
    console.error('固定URL提交失败:', error);
    ElMessage.error('固定URL提交失败：' + (error.response?.data?.message || error.message));
  }
};

// 提交密码修改
const submitPassword = async () => {
  try {
    await passwordFormRef.value.validate();

    const passwordData = {
      oldPassword: passwordForm.oldPassword,
      newPassword: passwordForm.newPassword
    };

    const response = await userApi.changePassword(passwordData);
    if (response.data?.code === 200) {
      ElMessage.success('密码修改成功，请重新登录');
      passwordForm.oldPassword = '';
      passwordForm.newPassword = '';
      passwordForm.confirmPassword = '';
      await userApi.logout();
      userStore.resetState();  // 使用resetState重置状态
      router.push('/login');
    } else {
      ElMessage.error('密码修改失败：' + (response.data?.message || '旧密码错误或格式不正确'));
    }
  } catch (error) {
    ElMessage.error('提交失败：' + (error.response?.data?.message || error.message));
  }
};
</script>

<style scoped>
.profile-edit-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.avatar-uploader {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.avatar-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-upload:hover {
  border-color: #409eff;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
  border-radius: 6px;
}

.avatar-placeholder {
  width: 178px;
  height: 178px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  color: #666;
  font-size: 24px;
}

.avatar-hint {
  margin-top: 10px;
  color: #666;
  font-size: 12px;
}

.profile-form, .password-form {
  margin-top: 20px;
}

.password-card {
  margin-top: 30px;
}
</style>