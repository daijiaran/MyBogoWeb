import axios from 'axios';
import { defineStore } from 'pinia';

/**
 * 清理Token中的非法字符
 */
const cleanToken = (rawToken) => {
    if (!rawToken) return '';
    return rawToken
        .replace(/\s+/g, '')
        // eslint-disable-next-line no-control-regex
        .replace(/[\x00-\x1F\x7F]/g, '')
        .replace(/\u00A0/g, '');
};

// 创建 axios 实例
const request = axios.create({
    baseURL: '/api',
    timeout: 60000
});

// 请求拦截器（统一处理Token）
request.interceptors.request.use(config => {
    const rawToken = localStorage.getItem('token');
    const cleanedToken = cleanToken(rawToken);
    if (cleanedToken) {
        config.headers.Authorization = `Bearer ${cleanedToken}`;
    }
    console.log('过滤后的Authorization头:', config.headers.Authorization);
    return config;
}, error => {
    return Promise.reject(error);
});

/**
 * 用户API集合
 */
const userApi = {
    register: (data) => request.post('/users/register', data),
    verifyCode: (data) => request.post('/users/verify-code', data),
    login: (data) => request.post('/users/login', data),
    logout: () => request.post('/users/logout'),
    forgotPassword: (email) => request.post('/users/forgot-password', null, { params: { email } }),
    resetPassword: (data) => request.post('/users/reset-password', data),
    changePassword: (data) => request.put('/users/change-password', data),
    getCurrentUser: () => request.get('/users/me'),
    /**
     * 通过用户ID获取用户信息
     * @param {string} userId - 用户ID (UUID字符串)
     * @returns {Promise} 返回用户信息响应
     */
    getUserById: (userId) => request.get(`/users/${userId}`),
    updateProfile: (data) => request.put('/users/profile', data)
};

/**
 * Pinia用户状态管理
 */
export const useUserStore = defineStore('user', {
    state: () => ({
        isLogin: false,
        username: '',
        avatarUrl: '',
        userId: '',
        loading: false,
        error: null,
        currentRegisterEmail: ''
    }),
    actions: {
        resetState() {
            this.isLogin = false;
            this.username = '';
            this.avatarUrl = '';
            this.userId = '';
            this.error = null;
            this.currentRegisterEmail = '';
        },

        async login(loginData) {
            try {
                this.loading = true;
                this.error = null;
                const response = await userApi.login(loginData);
                const result = response.data;

                if (result.code !== 200) {
                    throw new Error(result.message || '登录失败');
                }

                const { token, user } = result.data;
                const cleanedToken = cleanToken(token);
                localStorage.setItem('token', cleanedToken);

                this.isLogin = true;
                this.username = user.name;
                this.avatarUrl = user.avatarUrl || '/assets/default-avatar.png';
                this.userId = user.id;

                console.log('存储的纯净token:', localStorage.getItem('token'));
                return result.data;
            } catch (err) {
                this.error = err.response?.data?.message || err.message || '登录失败，请重试';
                throw err;
            } finally {
                this.loading = false;
            }
        },

        async logout() {
            try {
                this.loading = true;
                const response = await userApi.logout();
                const result = response.data;
                if (result.code !== 200) {
                    throw new Error(result.message || '登出失败');
                }
            } catch (err) {
                console.error('登出失败:', err.response?.data?.message || err.message);
            } finally {
                localStorage.removeItem('token');
                this.resetState();
                this.loading = false;
            }
        },

        async initUser() {
            const token = localStorage.getItem('token');
            if (!token) {
                this.resetState();
                return;
            }
            try {
                this.loading = true;
                const response = await userApi.getCurrentUser();
                const result = response.data;

                if (result.code !== 200) {
                    if (result.code === 401) {
                        localStorage.removeItem('token');
                        this.resetState();
                    } else {
                        console.warn('获取用户信息失败，但保留 token:', result.message);
                    }
                    return;
                }

                this.isLogin = true;
                this.username = result.data.name;
                this.avatarUrl = result.data.avatarUrl || '/assets/user-avatar.png';
                this.userId = result.data.id;
            } catch (err) {
                console.error('initUser 网络错误:', err);
            } finally {
                this.loading = false;
            }
        },

        async updateAvatar(avatarUrl) {
            try {
                this.loading = true;
                const response = await userApi.updateProfile({ avatarUrl });
                const result = response.data;

                if (result.code !== 200) {
                    throw new Error(result.message || '更新头像失败');
                }

                this.avatarUrl = avatarUrl;
                return true;
            } catch (err) {
                this.error = err.response?.data?.message || err.message || '更新头像失败';
                throw err;
            } finally {
                this.loading = false;
            }
        },

        async register(registerData) {
            try {
                this.loading = true;
                this.error = null;
                const response = await userApi.register(registerData);
                const result = response.data;

                if (result.code !== 200) {
                    throw new Error(result.message || '注册失败');
                }

                this.currentRegisterEmail = registerData.email;
                return result.data;
            } catch (err) {
                this.error = err.response?.data?.message || err.message || '注册失败，请检查信息';
                throw err;
            } finally {
                this.loading = false;
            }
        },

        async verifyRegistrationCode(code) {
            if (!this.currentRegisterEmail || !code) {
                this.error = '请输入验证码';
                return false;
            }

            try {
                this.loading = true;
                this.error = null;
                const response = await userApi.verifyCode({
                    email: this.currentRegisterEmail,
                    code: code
                });
                const result = response.data;

                if (result.code !== 200) {
                    throw new Error(result.message || '验证码验证失败');
                }

                this.currentRegisterEmail = '';
                return true;
            } catch (err) {
                this.error = err.response?.data?.message || err.message || '验证码错误或已过期';
                throw err;
            } finally {
                this.loading = false;
            }
        }
    }
});

export default userApi;