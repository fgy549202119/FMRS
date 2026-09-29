<!--
  维修人员布局组件 - StaffLayout.vue
  
  该组件是维修人员端的主布局组件，包含：
  - 顶部导航栏：显示系统标题、用户信息和下拉菜单
  - 左侧菜单栏：显示维修人员可访问的所有功能模块
  - 主内容区：渲染子路由组件
  
  功能模块：
  - 工作台：显示待处理工单和统计数据
  - 报修接单：查看和接受待处理工单
  - 我的工单：查看当前处理的工单
  - 公共设备：查看公共设备信息
  - 维修记录：查看维修历史记录
  - 维修知识库：查询维修知识
  - 设备巡检：执行设备巡检任务
  - 评价信息：查看用户对自己的评价
  - 个人中心：维修人员个人信息管理
  
  作者：FMRS开发团队
  创建日期：2024年
-->

<template>
  <!-- 维修人员布局容器 -->
  <div class="staff-layout">
    <!-- Element Plus容器组件 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <!-- 系统标题 -->
        <div class="logo">佳木斯大学设备管理与报修系统 - 维修员端</div>
        
        <!-- 右侧区域 -->
        <div class="header-right">
          <!-- 用户信息区域 -->
          <div class="user-info">
            <!-- 显示用户姓名 -->
            <span>{{ staffInfo.real_name }}</span>
            
            <!-- 用户头像下拉菜单 -->
            <el-dropdown @command="handleCommand">
              <el-avatar :src="staffInfo.avatar" :size="36" style="background: linear-gradient(135deg, #059669, #10b981); font-size: 16px;">
                {{ (staffInfo.real_name || '维')[0] }}
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
        </div>
      </el-header>
      
      <!-- 主体区域 -->
      <el-container>
        <!-- 左侧菜单栏 -->
        <el-aside width="200px">
          <!-- 导航菜单，使用router模式实现路由跳转 -->
          <el-menu :default-active="$route.path" router>
            <!-- 工作台 -->
            <el-menu-item index="/staff/home">
              <el-icon><HomeFilled /></el-icon>
              <span>工作台</span>
            </el-menu-item>
            
            <!-- 报修接单 -->
            <el-menu-item index="/staff/accept">
              <el-icon><DocumentChecked /></el-icon>
              <span>报修接单</span>
            </el-menu-item>
            
            <!-- 我的工单 -->
            <el-menu-item index="/staff/my-orders">
              <el-icon><List /></el-icon>
              <span>我的工单</span>
            </el-menu-item>
            
            <!-- 维修记录 -->
            <el-menu-item index="/staff/record">
              <el-icon><Document /></el-icon>
              <span>维修记录</span>
            </el-menu-item>
            
            <!-- 维修知识库 -->
            <el-menu-item index="/staff/knowledge">
              <el-icon><Reading /></el-icon>
              <span>维修知识库</span>
            </el-menu-item>
            
            <!-- 设备巡检 -->
            <el-menu-item index="/staff/inspection">
              <el-icon><View /></el-icon>
              <span>设备巡检</span>
            </el-menu-item>
            
            <!-- 评价信息 -->
            <el-menu-item index="/staff/evaluation">
              <el-icon><Star /></el-icon>
              <span>评价信息</span>
            </el-menu-item>
            
            <!-- 个人中心 -->
            <el-menu-item index="/staff/profile">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
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

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { staffApi } from '@/api'

// 获取路由实例
const router = useRouter()

// 维修人员信息响应式数据
// 从localStorage读取登录时存储的维修人员信息
const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))

/**
 * 处理下拉菜单命令
 * 
 * @param {string} command - 菜单命令（profile/logout）
 */
const handleCommand = (command) => {
  if (command === 'logout') {
    staffApi.logout().catch(() => {})
    localStorage.removeItem('staffToken')
    localStorage.removeItem('staffInfo')
    localStorage.removeItem('currentPortal')
    router.push('/login')
    ElMessage.success('退出成功')
  } else if (command === 'profile') {
    router.push('/staff/profile')
  }
}
</script>

<style scoped lang="scss">
.staff-layout {
  height: 100vh;
  
  .el-container {
    height: 100%;
  }
  
  .el-header {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 50%, #059669 100%);
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
        background: linear-gradient(180deg, #34d399, #10b981);
        border-radius: 4px;
      }
    }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 20px;
      
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
          background: #ecfdf5;
          color: #059669;
        }
        
        &.is-active {
          background: linear-gradient(135deg, #059669, #10b981);
          color: #fff;
          font-weight: 500;
          box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
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
