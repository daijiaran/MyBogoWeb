const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  publicPath: '/',
  outputDir: 'dist',
  assetsDir: 'static',
  productionSourceMap: false,
  // 注入环境变量
  chainWebpack: config => {
    config.plugin('define').tap(args => {
      args[0]['process.env'].VUE_APP_API_BASE_URL = JSON.stringify(process.env.VUE_APP_API_BASE_URL);
      return args;
    });
  },
  devServer: {
    port: 8082,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      '/images': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})