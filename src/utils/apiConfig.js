/**
 * 根据当前环境获取 API 基础地址
 * 开发环境使用 VUE_APP_API_BASE_URL_DEVELOP
 * 生产环境使用 VUE_APP_API_BASE_URL_RELEASE
 */
export function getApiBaseUrl() {
  // process.env.NODE_ENV 在 Vue CLI 中会自动注入
  const isDevelopment = process.env.NODE_ENV === 'development';

  if (isDevelopment) {
    return process.env.VUE_APP_API_BASE_URL_DEVELOP || 'http://localhost:8080';
  } else {
    return process.env.VUE_APP_API_BASE_URL_RELEASE || 'http:localhost:8443';
  }
}

// 导出常量，方便直接使用
export const API_BASE_URL = getApiBaseUrl();
