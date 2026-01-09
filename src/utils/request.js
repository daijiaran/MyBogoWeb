import axios from "axios";
import { getApiBaseUrl } from "./apiConfig";

// 创建 axios 实例
const service = axios.create({
    baseURL: getApiBaseUrl(),
    timeout: 10000
});

// 请求拦截器（可选）
service.interceptors.request.use(
    config => {
        // 你可以在这里添加 token 等
        return config;
    },
    error => {
        console.error("请求错误:", error);
        return Promise.reject(error);
    }
);

// 响应拦截器（返回 data）
service.interceptors.response.use(
    response => {
        // Spring Boot 返回的结构一般是 { code, message, data }
        return response.data;
    },
    error => {
        console.error("响应错误:", error);
        return Promise.reject(error);
    }
);

export default service;
