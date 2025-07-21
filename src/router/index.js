import { createRouter, createWebHistory } from 'vue-router'
// 导入各主题对应的组件（根据实际需求创建这些组件）
import Home from '../views/HomeView.vue'       // 首页组件
import Works from '../views/WorksView.vue'     // 作品页面组件
import LifeLog from '../views/LifeLogView.vue' // 生活日志组件
import Manage from '../views/ManageView.vue'
import ArticleView from "@/views/ArticleView.vue";
import ActivateView from "@/views/ActivateView.vue";
import UserView from "@/views/UserView.vue";   // 管理页面组件

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home  // 首页对应的组件
    },
    {
        path: '/about',
        name: 'Works',
        component: Works  // 作品页面对应的组件
    },
    {
        path: '/products',
        name: 'LifeLog',
        component: LifeLog  // 生活日志对应的组件
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
        path: '/activate',
        name: 'Activate',
        component: ActivateView
    },
    {
        path: '/user',
        name: 'User',
        component: UserView
    }

]

const router = createRouter({
    history: createWebHistory(),  // 使用HTML5 history模式
    routes
})

export default router
