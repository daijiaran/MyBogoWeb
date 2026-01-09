// vue.config.js
const isDevelopment = process.env.NODE_ENV === 'development';

module.exports = {
  publicPath: './', // 保证生产环境路径正确

  configureWebpack: {
    plugins: [
      new (require('webpack')).DefinePlugin({
        'import.meta.env.VITE_API_BASE_URL': JSON.stringify(
            isDevelopment
                ? (process.env.VITE_API_BASE_URL_develop || 'http://localhost:8080')
                : '/api' // 生产环境通过 Nginx 代理
        )
      })
    ]
  },

  devServer: {
    port: 8082,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // 开发环境后端地址
        changeOrigin: true
      },
      '/images': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
};
