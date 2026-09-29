<!--
  登录页面 - Login.vue
  
  该组件是系统的登录页面，支持三种身份登录：用户、维修人员、管理员。
  主要功能：
  - 提供三种身份的登录表单
  - 表单验证
  - 登录状态管理（token存储）
  - 跳转至对应角色的首页
  
  组件结构：
  - template：包含登录表单、标签页切换
  - script：包含表单数据、验证规则、登录逻辑
  - style：包含登录页面的视觉样式
  
  作者：FMRS系统开发者-范广宇
  创建日期：2026年
-->

<template>
  <div class="login-page">
    <div class="login-container">
      <!-- 登录页面标题 -->
      <div class="login-header">
        <h2>佳木斯大学设备管理与报修系统</h2>
        <p>请选择登录身份</p>
      </div>
      
      <!-- 登录身份标签页 -->
      <el-tabs v-model="loginType" class="login-tabs">
        <!-- 用户登录标签 -->
        <el-tab-pane label="用户登录" name="user">
          <el-form :model="userForm" :rules="userRules" ref="userFormRef">
            <el-form-item prop="username">
              <el-input v-model="userForm.username" placeholder="请输入学号/教师号" prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="userForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUserLogin" :loading="loading" style="width: 100%">登录</el-button>
            </el-form-item>
            <el-form-item>
              <span>还没有账号？</span>
              <el-button type="text" @click="$router.push('/register')">立即注册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 维修员登录标签 -->
        <el-tab-pane label="维修员登录" name="staff">
          <el-form :model="staffForm" :rules="staffRules" ref="staffFormRef">
            <el-form-item prop="staff_no">
              <el-input v-model="staffForm.staff_no" placeholder="请输入手机号" prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="staffForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleStaffLogin" :loading="loading" style="width: 100%">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 管理员登录标签 -->
        <el-tab-pane label="管理员登录" name="admin">
          <el-form :model="adminForm" :rules="adminRules" ref="adminFormRef">
            <el-form-item prop="admin_no">
              <el-input v-model="adminForm.admin_no" placeholder="请输入管理员账号" prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="adminForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAdminLogin" :loading="loading" style="width: 100%">登录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 返回首页按钮 -->
      <div class="back-home">
        <el-button type="text" @click="$router.push('/')">返回首页</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 登录页面脚本
 * 
 * 使用Vue 3的组合式API（Composition API）编写。
 * 主要功能：
 * - 管理登录表单数据和验证规则
 * - 处理三种身份的登录逻辑
 * - 登录成功后存储token和用户信息
 * - 登录成功后跳转到对应角色的首页
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { userApi, staffApi, adminApi } from '@/api'
import { ElMessage } from 'element-plus'

const router = useRouter()

/**
 * 加载状态
 * @type {Ref<boolean>}
 */
const loading = ref(false)

/**
 * 当前登录类型
 * @type {Ref<string>} 'user' | 'staff' | 'admin'
 */
const loginType = ref('user')

/**
 * 用户登录表单引用
 * @type {Ref<FormInstance>}
 */
const userFormRef = ref()

/**
 * 维修人员登录表单引用
 * @type {Ref<FormInstance>}
 */
const staffFormRef = ref()

/**
 * 管理员登录表单引用
 * @type {Ref<FormInstance>}
 */
const adminFormRef = ref()

/**
 * 用户登录表单数据
 * @type {Object}
 */
const userForm = reactive({
  username: '', // 学号/教师号
  password: ''  // 密码
})

/**
 * 维修人员登录表单数据
 * @type {Object}
 */
const staffForm = reactive({
  staff_no: '', // 手机号
  password: ''  // 密码
})

/**
 * 管理员登录表单数据
 * @type {Object}
 */
const adminForm = reactive({
  admin_no: '', // 管理员账号
  password: ''  // 密码
})

/**
 * 用户登录表单验证规则
 * @type {Object}
 */
const userRules = {
  username: [{ required: true, message: '请输入学号/教师号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

/**
 * 维修人员登录表单验证规则
 * @type {Object}
 */
const staffRules = {
  staff_no: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

/**
 * 管理员登录表单验证规则
 * @type {Object}
 */
const adminRules = {
  admin_no: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

/**
 * 处理用户登录
 * @async
 * @returns {Promise<void>}
 */
const handleUserLogin = async () => {
  // 验证表单
  await userFormRef.value.validate()
  loading.value = true
  try {
    // 调用用户登录API
    const res = await userApi.login(userForm)
    if (res.code === 200) {
      // 存储token和用户信息
      localStorage.setItem('userToken', res.token)
      localStorage.setItem('userInfo', JSON.stringify(res.data))
      localStorage.setItem('currentPortal', 'user')
      ElMessage.success('登录成功')
      // 跳转到用户首页
      router.push('/user/home')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}

/**
 * 处理维修员登录
 * @async
 * @returns {Promise<void>}
 */
const handleStaffLogin = async () => {
  // 验证表单
  await staffFormRef.value.validate()
  loading.value = true
  try {
    // 调用维修人员登录API
    const res = await staffApi.login(staffForm)
    if (res.code === 200) {
      // 存储token和维修人员信息
      localStorage.setItem('staffToken', res.token)
      localStorage.setItem('staffInfo', JSON.stringify(res.data))
      localStorage.setItem('currentPortal', 'staff')
      ElMessage.success('登录成功')
      // 跳转到维修人员首页
      router.push('/staff/home')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}

/**
 * 处理管理员登录
 * @async
 * @returns {Promise<void>}
 */
const handleAdminLogin = async () => {
  // 验证表单
  await adminFormRef.value.validate()
  loading.value = true
  try {
    // 调用管理员登录API
    const res = await adminApi.login(adminForm)
    if (res.code === 200) {
      // 存储token和管理员信息
      localStorage.setItem('adminToken', res.token)
      localStorage.setItem('adminInfo', JSON.stringify(res.data))
      localStorage.setItem('currentPortal', 'admin')
      ElMessage.success('登录成功')
      // 跳转到管理员首页
      router.push('/admin/home')
    } else {
      ElMessage.error(res.message || '登录失败')
    }
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
/**
 * 登录页面样式
 * 
 * 采用深蓝渐变背景，毛玻璃卡片效果，响应式设计。
 * 包含：
 * - 动态背景光晕效果
 * - 登录卡片悬浮动画
 * - 输入框聚焦效果
 * - 按钮悬浮效果
 */
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 40%, #312e81 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 70% 30%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
    animation: bgFloat 20s ease-in-out infinite;
  }
  
  @keyframes bgFloat {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-2%, -1%); }
  }
  
  .login-container {
    width: 420px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: var(--radius-2xl);
    padding: 40px 36px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1);
    position: relative;
    z-index: 1;
    animation: fadeInUp 0.5s ease forwards;
    
    .login-header {
      text-align: center;
      margin-bottom: 32px;
      
      h2 {
        font-size: 22px;
        color: var(--gray-800);
        margin-bottom: 8px;
        font-weight: 700;
        letter-spacing: -0.3px;
      }
      
      p {
        color: var(--gray-500);
        font-size: 14px;
      }
    }
    
    .login-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 24px;
      }
      
      :deep(.el-tabs__nav-wrap::after) {
        display: none;
      }
      
      :deep(.el-tabs__active-bar) {
        background: linear-gradient(90deg, #4f46e5, #6366f1);
        height: 3px;
        border-radius: 3px;
      }
      
      :deep(.el-tabs__item) {
        font-size: 15px;
        font-weight: 500;
        color: var(--gray-400);
        
        &.is-active {
          color: #4f46e5;
        }
        
        &:hover {
          color: #6366f1;
        }
      }
      
      :deep(.el-form-item) {
        margin-bottom: 20px;
      }
      
      :deep(.el-input__wrapper) {
        border-radius: var(--radius-md);
        padding: 4px 12px;
        box-shadow: 0 0 0 1px var(--gray-200) inset;
        
        &:hover {
          box-shadow: 0 0 0 1px var(--gray-300) inset;
        }
        
        &.is-focus {
          box-shadow: 0 0 0 2px #6366f1 inset;
        }
      }
      
      :deep(.el-button--primary) {
        height: 44px;
        font-size: 15px;
        background: linear-gradient(135deg, #4f46e5, #6366f1);
        border: none;
        border-radius: var(--radius-md);
        transition: all var(--transition-normal);
        
        &:hover {
          background: linear-gradient(135deg, #4338ca, #4f46e5);
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
        }
        
        &:active {
          transform: translateY(0);
        }
      }
    }
    
    .back-home {
      text-align: center;
      margin-top: 20px;
      
      :deep(.el-button--text) {
        color: var(--gray-400);
        font-size: 13px;
        
        &:hover {
          color: #6366f1;
        }
      }
    }
  }
}
</style>
