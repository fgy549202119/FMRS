/**
 * Vue应用入口文件
 * 
 * 该文件是前端应用的启动入口，负责创建和配置Vue应用实例。
 * 主要功能：
 * - 创建Vue应用实例
 * - 注册全局插件（Pinia状态管理、Vue Router路由、Element Plus组件库）
 * - 注册Element Plus图标组件
 * - 配置中文语言包
 * - 挂载应用到DOM
 * 
 * 技术栈：
 * - Vue 3：渐进式JavaScript框架
 * - Pinia：Vue官方状态管理库
 * - Vue Router：Vue官方路由管理器
 * - Element Plus：基于Vue 3的组件库
 * 
 * 作者：FMRS开发团队
 * 创建日期：2024年
 */

// 导入Vue应用创建函数
import { createApp } from 'vue'

// 导入Pinia状态管理库
import { createPinia } from 'pinia'

// 导入Element Plus组件库及其样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 导入Element Plus中文语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 导入Element Plus图标库
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 导入根组件
import App from './App.vue'

// 导入路由配置
import router from './router'

// 导入全局样式
import './styles/index.scss'

// 创建Vue应用实例
const app = createApp(App)

// 全局注册Element Plus图标组件
// 遍历所有图标组件，注册为全局组件
// 使用方式：<el-icon><Edit /></el-icon>
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册Pinia状态管理插件
app.use(createPinia())

// 注册Vue Router路由插件
app.use(router)

// 注册Element Plus组件库，配置中文语言
app.use(ElementPlus, { locale: zhCn })

// 将应用挂载到index.html中的#app元素
app.mount('#app')
