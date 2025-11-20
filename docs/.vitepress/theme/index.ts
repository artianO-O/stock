import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'
import './custom.css'

export default {
  ...DefaultTheme,
  Layout: Layout,
  enhanceApp({ app }) {
    // 可以在这里注册全局组件
  }
}
