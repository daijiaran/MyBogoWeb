import {createRouter, createWebHashHistory} from 'vue-router'
// 导入各主题对应的组件（根据实际需求创建这些组件）
import Home from '../views/HomeView.vue'       // 首页组件
import UnityProjectView from '../views/UnityProjectView.vue'     // 作品页面组件
import PromotionalVideoView from '../views/PromotionalVideoView.vue' // 生活日志组件
import Manage from '../views/ManageView.vue'
import ArticleView from "@/views/ArticleView.vue";
import UserView from "@/views/UserView.vue";
import LogView from "@/views/LogView.vue";   // 管理页面组件
import ExamTool from "@/components/Pages/quiz-app-container.vue"
import SQLView from "@/components/Pages/SQL.vue"

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home  // 首页对应的组件
    },
    {
        path: '/UnityProject',
        name: 'UnityProject',
        component: UnityProjectView  // 作品页面对应的组件
    },
    {
        path: '/PromotionalVideoView',
        name: 'PromotionalVideo',
        component: PromotionalVideoView  // 生活日志对应的组件
    },
    {
        path: '/manage',  // 修正原导航中"管理"的重复路径
        name: 'Manage',
        component: Manage  // 管理页面对应的组件
    },
    {
        path: '/article/:id',
        name: 'Article',
        component: ArticleView,
        props: true
    },
    {
        path: '/LogView',
        name: 'LogView',
        component: LogView
    },
    {
        path: '/quiz-app-container',
        name: 'ExamTool',
        component: ExamTool
    },
    {
        path: '/user',
        name: 'User',
        component: UserView
    },
    {
        path: '/sql',
        name: 'SQL',
        component: SQLView
    }

]

const router = createRouter({
    // history: createWebHistory(),  // 使用HTML5 history模式
    history: createWebHashHistory(),
    routes
})

export default router
