<!--
  管理员布局组件 - AdminLayout.vue
  
  该组件是管理员端的主布局组件，包含：
  - 顶部导航栏：显示系统标题、用户信息和下拉菜单
  - 左侧菜单栏：显示管理员可访问的所有功能模块
  - 主内容区：渲染子路由组件
  
  功能模块：
  - 系统首页：系统概览和快捷入口
  - 统计分析：数据统计和图表展示
  - 用户管理：管理普通用户账号
  - 维修员管理：管理维修员账号
  - 设备类型：管理设备分类
  - 校园位置管理：管理校区、楼栋、楼层
  - 公共设备：管理设备信息
  - 设备报修：查看和管理报修工单
  - 维修记录：查看维修历史记录
  - 备件库存：管理备件出入库
  - 维修知识库：管理维修知识条目
  - 评价信息：查看和管理用户评价
  - 设备巡检：管理巡检任务
  - 校园公告：发布系统公告
  - 数据导出：导出Excel/PDF报表
  - 个人中心：管理员个人信息管理
  
  作者：FMRS开发团队
  创建日期：2024年
-->

<template>
  <!-- 管理员布局容器 -->
  <div class="admin-layout">
    <!-- Element Plus容器组件 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header>
        <!-- 系统标题 -->
        <div class="logo">佳木斯大学设备管理与报修系统 - 管理员端</div>
        
        <!-- 用户信息区域 -->
        <div class="user-info">
          <!-- 显示用户姓名 -->
          <span>{{ adminInfo.real_name }}</span>
          
          <!-- 用户头像下拉菜单 -->
          <el-dropdown @command="handleCommand">
            <el-avatar :src="adminInfo.avatar" :size="36" style="background: linear-gradient(135deg, #1e40af, #3b82f6); font-size: 16px;">
              {{ (adminInfo.real_name || '管')[0] }}
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
            <!-- 系统首页 -->
            <el-menu-item index="/admin/home">
              <el-icon><HomeFilled /></el-icon>
              <span>系统首页</span>
            </el-menu-item>
            
            <!-- 统计分析 -->
            <el-menu-item index="/admin/statistics">
              <el-icon><DataAnalysis /></el-icon>
              <span>统计分析</span>
            </el-menu-item>
            
            <!-- 用户管理 -->
            <el-menu-item index="/admin/users">
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            
            <!-- 维修员管理 -->
            <el-menu-item index="/admin/staff">
              <el-icon><Avatar /></el-icon>
              <span>维修员管理</span>
            </el-menu-item>
            
            <!-- 设备类型 -->
            <el-menu-item index="/admin/equipment-type">
              <el-icon><Grid /></el-icon>
              <span>设备类型</span>
            </el-menu-item>
            
            <!-- 校园位置管理 -->
            <el-menu-item index="/admin/location">
              <el-icon><Location /></el-icon>
              <span>校园位置管理</span>
            </el-menu-item>
            
            <!-- 公共设备 -->
            <el-menu-item index="/admin/equipment">
              <el-icon><Monitor /></el-icon>
              <span>公共设备</span>
            </el-menu-item>
            
            <!-- 设备报修 -->
            <el-menu-item index="/admin/repair-order">
              <el-icon><Tools /></el-icon>
              <span>设备报修</span>
            </el-menu-item>
            
            <!-- 维修记录 -->
            <el-menu-item index="/admin/record">
              <el-icon><Document /></el-icon>
              <span>维修记录</span>
            </el-menu-item>
            
            <!-- 备件库存 -->
            <el-menu-item index="/admin/spare-part">
              <el-icon><Box /></el-icon>
              <span>备件库存</span>
            </el-menu-item>
            
            <!-- 维修知识库 -->
            <el-menu-item index="/admin/knowledge">
              <el-icon><Reading /></el-icon>
              <span>维修知识库</span>
            </el-menu-item>
            
            <!-- 评价信息 -->
            <el-menu-item index="/admin/evaluation">
              <el-icon><Star /></el-icon>
              <span>评价信息</span>
            </el-menu-item>
            
            <!-- 设备巡检 -->
            <el-menu-item index="/admin/inspection">
              <el-icon><View /></el-icon>
              <span>设备巡检</span>
            </el-menu-item>
            
            <!-- 校园公告 -->
            <el-menu-item index="/admin/announcement">
              <el-icon><Bell /></el-icon>
              <span>校园公告</span>
            </el-menu-item>
            
            <!-- 留言管理 -->
            <el-menu-item index="/admin/message-board">
              <el-icon><ChatDotSquare /></el-icon>
              <span>留言管理</span>
            </el-menu-item>
            
            <!-- 数据导出 -->
            <el-menu-item index="/admin/export">
              <el-icon><Download /></el-icon>
              <span>数据导出</span>
            </el-menu-item>
            
            <!-- 个人中心 -->
            <el-menu-item index="/admin/profile">
              <el-icon><Setting /></el-icon>
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
import { adminApi } from '@/api'

// 导入Element Plus图标组件
import { Box, Reading, Download, Grid, HomeFilled, DataAnalysis, User, Avatar, Monitor, Tools, Document, Star, View, Bell, Setting, Location } from '@element-plus/icons-vue'

// 获取路由实例
const router = useRouter()

// 管理员信息响应式数据
// 从localStorage读取登录时存储的管理员信息
const adminInfo = ref(JSON.parse(localStorage.getItem('adminInfo') || '{}'))

/**
 * 处理下拉菜单命令
 * 
 * @param {string} command - 菜单命令（profile/logout）
 */
const handleCommand = (command) => {
  if (command === 'logout') {
    adminApi.logout().catch(() => {})
    localStorage.removeItem('adminToken')
    localStorage.removeItem('adminInfo')
    localStorage.removeItem('currentPortal')
    router.push('/login')
    ElMessage.success('退出成功')
  } else if (command === 'profile') {
    router.push('/admin/profile')
  }
}
</script>

<style scoped lang="scss">
.admin-layout {
  height: 100vh;
  
  .el-container {
    height: 100%;
  }
  
  .el-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e40af 100%);
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
        background: linear-gradient(180deg, #60a5fa, #3b82f6);
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
          background: var(--primary-50);
          color: var(--primary-600);
        }
        
        &.is-active {
          background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
          color: #fff;
          font-weight: 500;
          box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
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
