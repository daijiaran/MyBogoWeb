import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'
import { Message } from 'element-plus';
import { createPinia } from 'pinia'
// 创建Pinia实例
const pinia = createPinia()

// 1. 导入 Element Plus 图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 导入 markdown 编辑器
import { VMdEditor } from './plugins/v-md-editor'

const app = createApp(App)

app.config.globalProperties.$message = Message;

// 2. 全局注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

// axios 配置
axios.defaults.baseURL = 'http://localhost:8080'
axios.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
}, error => Promise.reject(error))

// 注册插件
app.use(ElementPlus)
app.use(router)
app.use(pinia)
app.component('v-md-editor', VMdEditor)

app.config.globalProperties.$axios = axios

app.mount('#app')