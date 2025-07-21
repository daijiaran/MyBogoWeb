// vue.config.js
const webpack = require('webpack');

module.exports = {
  configureWebpack: {
    resolve: {
      // 让 webpack 能自动解析这些扩展名，无需每次写 .ts/.js/.vue
      extensions: ['.ts', '.js', '.vue', '.json']
    },
    plugins: [
      new webpack.ProgressPlugin({
        activeModules: false,
        entries: true,
        modules: true
      })
    ]
  },

  // 开发服务器配置
  devServer: {
    port: 8082, // 前端开发端口，可根据需要修改
    open: true, // 启动时自动打开浏览器
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // 后端接口地址
        changeOrigin: true,              // 修改请求头中的 origin
        pathRewrite: { '^/api': '/api' } // 可选：保留 /api 前缀
      },

      '/images': {  // 匹配以 /images 开头的请求
        target: 'http://localhost:8080',  // 转发到后端 8080 端口
        changeOrigin: true,  // 允许跨域
        pathRewrite: {'^/images': '/images'}  // 保持路径不变
      }

    }


  }
};
