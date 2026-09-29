<!--
  普通用户布局组件 - UserLayout.vue
  
  该组件是普通用户端的主布局组件，包含：
  - 顶部导航栏：显示系统标题、用户信息和下拉菜单
  - 左侧菜单栏：显示用户可访问的所有功能模块
  - 主内容区：渲染子路由组件
  
  功能模块：
  - 个人中心：显示用户概览和快捷入口
  - 设备报修：提交报修请求
  - 报修记录：查看报修历史和进度
  - 评价信息：查看和提交评价
  - 个人信息：用户个人信息管理
  
  AI助手功能：
  - 部署阿里云百炼AI助手悬浮挂件
  - 用户登录后自动加载，未登录不加载
  - 动态注入用户Token完成身份认证
  - 退出登录时自动清理AI助手资源
  
  作者：FMRS系统开发者-范广宇
  创建日期：2026年
-->

<template>
  <!-- 用户布局容器 -->
  <div class="user-layout">
    <!-- Element Plus容器组件 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <!-- 系统标题 -->
        <div class="logo">佳木斯大学设备管理与报修系统</div>
        
        <!-- 用户信息区域 -->
        <div class="user-info">
          <!-- 显示用户姓名 -->
          <span>{{ userInfo.real_name }}</span>
          
          <!-- 用户头像下拉菜单 -->
          <el-dropdown @command="handleCommand">
            <el-avatar :src="userInfo.avatar" :size="36" style="background: linear-gradient(135deg, #4f46e5, #6366f1); font-size: 16px;">
              {{ (userInfo.real_name || '用')[0] }}
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <!-- 个人中心菜单项 -->
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <!-- 退出登录菜单项 -->
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 主体区域 -->
      <el-container>
        <!-- 左侧菜单栏 -->
        <el-aside width="200px">
          <!-- 导航菜单，使用router模式实现路由跳转 -->
          <el-menu :default-active="$route.path" router>
            <!-- 个人中心 -->
            <el-menu-item index="/user/home">
              <el-icon><HomeFilled /></el-icon>
              <span>个人中心</span>
            </el-menu-item>
            
            <!-- 设备报修 -->
            <el-menu-item index="/user/repair">
              <el-icon><Tools /></el-icon>
              <span>设备报修</span>
            </el-menu-item>
            
            <!-- 报修记录 -->
            <el-menu-item index="/user/repair-list">
              <el-icon><Document /></el-icon>
              <span>报修记录</span>
            </el-menu-item>
            
            <!-- 评价信息 -->
            <el-menu-item index="/user/evaluation">
              <el-icon><Star /></el-icon>
              <span>评价信息</span>
            </el-menu-item>
            
            <!-- 个人信息 -->
            <el-menu-item index="/user/profile">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </el-menu-item>
            
            <!-- 留言板 -->
            <el-menu-item index="/user/message-board">
              <el-icon><ChatDotSquare /></el-icon>
              <span>留言板</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <!-- 主内容区，渲染子路由组件 -->
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
/**
 * 组件脚本
 * 
 * 使用Vue 3的组合式API（Composition API）编写。
 */

import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { userApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const userInfo = ref({})

onMounted(async () => {
  try {
    const res = await userApi.profile()
    if (res.code === 200) {
      userInfo.value = res.data
    }
  } catch (error) {
    console.error(error)
  }

  // 增加延时确保页面完全挂载
  setTimeout(() => {
    initAIAssistant()
  }, 500)
})

onBeforeUnmount(() => {
  removeAIAssistant()
})

// 监听路由变化，路由切换后重新初始化AI助手
watch(() => route.path, () => {
  setTimeout(() => {
    initAIAssistant()
  }, 300)
})

/**
 * 初始化AI助手悬浮挂件
 * 
 * 功能说明：
 * - 从localStorage获取用户Token，未登录则不加载
 * - 动态创建script标签加载阿里云百炼AppflowChatSDK
 * - SDK加载完成后，使用用户Token初始化AI助手
 * - 集成ID和请求域名已在需求中配置，无需修改
 * 
 * 注意：此函数仅在用户登录后调用，确保未登录用户不会加载AI助手
 */
function initAIAssistant() {
  // 1. 排查token获取逻辑：尝试多种可能的键名
  let token = localStorage.getItem('userToken') || localStorage.getItem('token') || localStorage.getItem('accessToken')
  if (!token) {
    return
  }

  const existingScript = document.getElementById('appflow-chat-sdk')
  if (existingScript) {
    if (window.APPFLOW_CHAT_SDK) {
      initSDK(token)
    }
    return
  }

  const script = document.createElement('script')
  script.id = 'appflow-chat-sdk'
  script.src = 'https://o.alicdn.com/appflow/chatbot/v1/AppflowChatSDK.js'
  script.onload = () => {
    if (window.APPFLOW_CHAT_SDK) {
      initSDK(token)
    }
  }
  script.onerror = () => {}
  document.body.appendChild(script)
}

/**
 * 初始化SDK
 * @param {string} token - 用户Token
 */
function initSDK(token) {
  window.APPFLOW_CHAT_SDK.init({
    integrateConfig: {
      integrateId: 'cit-38e87fab447c430a92e3',
      domain: {
        requestDomain: 'https://ai.kebumt.cn'
      },
      access_session_token: token
    }
  })
  
  // 5. 排查样式遮挡：确保AI挂件z-index足够
  setTimeout(() => {
    const chatContainer = document.querySelector('#appflow-chat-container')
    if (chatContainer) {
      chatContainer.style.zIndex = '999999'
    }
  }, 1000)
}

/**
 * 移除AI助手悬浮挂件
 * 
 * 功能说明：
 * - 移除注入的SDK script标签
 * - 移除SDK创建的聊天容器DOM元素
 * - 在组件卸载或用户退出登录时调用，防止内存泄漏
 */
function removeAIAssistant() {
  const script = document.getElementById('appflow-chat-sdk')
  if (script) {
    script.remove()
  }
  const container = document.querySelector('#appflow-chat-container')
  if (container) {
    container.remove()
  }
}

/**
 * 处理下拉菜单命令
 * 
 * @param {string} command - 菜单命令（profile/logout）
 */
const handleCommand = (command) => {
  if (command === 'logout') {
    removeAIAssistant()
    userApi.logout().catch(() => {})
    localStorage.removeItem('userToken')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('currentPortal')
    router.push('/login')
    ElMessage.success('退出成功')
  } else if (command === 'profile') {
    router.push('/user/profile')
  }
}
</script>

<style scoped lang="scss">
.user-layout {
  height: 100vh;
  
  .el-container {
    height: 100%;
  }
  
  .el-header {
    background: linear-gradient(135deg, #312e81 0%, #4338ca 50%, #6366f1 100%);
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    height: 56px !important;
    padding: 0 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    position: relative;
    z-index: 10;
    
    .logo {
      font-size: 17px;
      font-weight: 700;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
      
      &::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 28px;
        background: linear-gradient(180deg, #a5b4fc, #6366f1);
        border-radius: 4px;
      }
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      
      span {
        font-size: 14px;
        opacity: 0.9;
      }
      
      .el-avatar {
        cursor: pointer;
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: border-color var(--transition-fast);
        
        &:hover {
          border-color: rgba(255, 255, 255, 0.7);
        }
      }
    }
  }
  
  .el-aside {
    background: #fff;
    border-right: none;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
    height: calc(100vh - 56px);
    overflow-y: auto;
    
    &::-webkit-scrollbar {
      width: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: var(--gray-200);
      border-radius: 4px;
    }
    
    .el-menu {
      border-right: none;
      padding: 8px;
      
      .el-menu-item {
        border-radius: var(--radius-md);
        margin-bottom: 2px;
        height: 44px;
        line-height: 44px;
        font-size: 14px;
        color: var(--gray-600);
        transition: all var(--transition-fast);
        
        .el-icon {
          font-size: 18px;
          margin-right: 8px;
        }
        
        &:hover {
          background: #eef2ff;
          color: #4f46e5;
        }
        
        &.is-active {
          background: linear-gradient(135deg, #4f46e5, #6366f1);
          color: #fff;
          font-weight: 500;
          box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }
      }
    }
  }
  
  .el-main {
    background: var(--gray-50);
    padding: 24px;
    min-height: calc(100vh - 56px);
  }
}
</style>
