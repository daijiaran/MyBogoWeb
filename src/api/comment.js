// comment.js - 评论相关API调用封装
import axios from 'axios';

// 创建axios实例，配置基础URL和超时时间
const commentApi = axios.create({
    baseURL: '/api', // 基础URL，对应后端接口的根路径
    timeout: 5000, // 请求超时时间
    headers: {
        'Content-Type': 'application/json'
    }
});

// 请求拦截器：添加认证token（如果需要）
commentApi.interceptors.request.use(
    config => {
        // 从localStorage获取token，实际项目中根据认证方式调整
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

/**
 * 提交评论
 * @param {Object} commentData - 评论数据
 * @param {string} commentData.content - 评论内容
 * @param {string} commentData.articleId - 文章ID（UUID）
 * @param {string} commentData.userId - 评论用户ID（UUID）
 * @param {string|null} commentData.parentId - 父评论ID（UUID，顶级评论为null）
 * @param {string} commentData.replyUserId - 被回复用户ID（UUID）
 * @returns {Promise<Object>} 包含新增评论信息的响应对象
 */
export const createComment = async (commentData) => {
    try {
        const response = await commentApi.post('/comments', commentData);
        return response.data;
    } catch (error) {
        console.error('提交评论失败:', error.response?.data || error.message);
        throw error;
    }
};

/**
 * 获取文章的评论（分页）
 * @param {string} articleId - 文章ID（UUID）
 * @param {number} page - 页码（从0开始，默认0）
 * @param {number} size - 每页条数（默认10）
 * @returns {Promise<Object>} 包含分页评论列表的响应对象
 */
export const getArticleComments = async (articleId, page = 0, size = 10) => {
    try {
        const response = await commentApi.get(`/comments/article/${articleId}`, {
            params: { page, size }
        });
        return response.data;
    } catch (error) {
        console.error('获取文章评论失败:', error.response?.data || error.message);
        throw error;
    }
};

/**
 * 获取评论的子评论
 * @param {string} parentId - 父评论ID（UUID）
 * @returns {Promise<Object>} 包含子评论列表的响应对象
 */
export const getChildComments = async (parentId) => {
    try {
        const response = await commentApi.get(`/comments/${parentId}/children`);
        return response.data;
    } catch (error) {
        console.error('获取子评论失败:', error.response?.data || error.message);
        throw error;
    }
};

export default {
    createComment,
    getArticleComments,
    getChildComments
};