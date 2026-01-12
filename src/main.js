import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import { Message } from 'element-plus';
import { createPinia } from 'pinia'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { VMdEditor } from './plugins/v-md-editor'

// --- 新增：获取环境变量中的服务器地址 ---
// 在 .env.production 中配置，见下文
const serverUrl = process.env.VUE_APP_API_BASE_URL || '';

const app = createApp(App)
const pinia = createPinia()

app.config.globalProperties.$message = Message;

// --- 新增：全局图片路径处理函数 ---
// 用法：<img :src="$img(article.cover)" />
app.config.globalProperties.$img = (url) => {
    if (!url) return '';
    // 1. 如果已经是完整网络连接或Base64，直接返回
    if (url.startsWith('http') || url.startsWith('https') || url.startsWith('data:')) {
        return url;
    }
    // 2. 如果是生产环境(App打包后) 且 url 以 / 开头，拼接服务器地址
    // 解决 App 端 file:// 协议找不到 /images/xxx.jpg 的问题
    if (process.env.NODE_ENV === 'production' && url.startsWith('/')) {
        // 去除可能重复的 /api 前缀（视你后端返回的路径而定）
        return `${serverUrl}${url}`;
    }
    // 3. 开发环境(Web)直接返回，走 devServer 代理
    return url;
}

// 注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

// --- 修改：Axios 配置 ---
// 生产环境(App)使用完整URL，开发环境使用相对路径
axios.defaults.baseURL = process.env.NODE_ENV === 'production'
    ? `${serverUrl}/api`
    : '/api';

axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
}, error => Promise.reject(error))

// 建议：添加响应拦截器，方便在手机端调试错误
axios.interceptors.response.use(
    res => res,
    error => {
        // 在手机上弹出错误提示
        if (process.env.NODE_ENV === 'production') {
            Message.error(error.message || '网络请求失败');
        }
        return Promise.reject(error);
    }
)

app.use(ElementPlus)
app.use(router)
app.use(pinia)
app.component('v-md-editor', VMdEditor)

app.config.globalProperties.$axios = axios

app.mount('#app')