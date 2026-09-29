/**
 * Vue Router 路由配置文件
 * 
 * 该文件定义了设施管理与报修系统(FMRS)的前端路由结构。
 * 采用嵌套路由的方式组织页面，支持三种用户角色：
 * - 普通用户（User）：提交报修、查看进度、评价服务
 * - 维修人员（Staff）：接单、处理工单、设备巡检
 * - 管理员（Admin）：系统管理、数据统计、人员管理
 * 
 * 路由结构：
 * - /                  -> 首页（公共页面）
 * - /login             -> 登录页
 * - /register          -> 注册页
 * - /user/*            -> 普通用户模块
 * - /staff/*           -> 维修人员模块
 * - /admin/*           -> 管理员模块
 * 
 * 技术特点：
 * - 使用路由懒加载（动态导入），优化首屏加载性能
 * - 使用meta字段存储页面标题
 * - 全局路由守卫设置页面标题
 * 
 * 作者：FMRS开发团队
 * 创建日期：2024年
 */

import { createRouter, createWebHistory } from 'vue-router'

/**
 * 路由配置数组
 * 
 * 定义应用的所有路由规则，每个路由包含：
 * - path: 路由路径
 * - name: 路由名称（用于编程式导航）
 * - component: 路由组件（使用懒加载）
 * - meta: 路由元信息（如页面标题）
 * - redirect: 重定向目标
 * - children: 子路由列表
 */
const routes = [
  // ========== 公共页面 ==========
  {
    // 首页
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    // 登录页
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    // 注册页
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册' }
  },
  
  // ========== 普通用户模块 ==========
  {
    // 用户布局路由
    path: '/user',
    name: 'UserLayout',
    component: () => import('@/layouts/UserLayout.vue'),
    redirect: '/user/home',  // 默认重定向到个人中心
    children: [
      {
        // 个人中心
        path: 'home',
        name: 'UserHome',
        component: () => import('@/views/user/Home.vue'),
        meta: { title: '个人中心' }
      },
      {
        // 设备报修页面
        path: 'repair',
        name: 'UserRepair',
        component: () => import('@/views/user/Repair.vue'),
        meta: { title: '设备报修' }
      },
      {
        // 报修记录列表
        path: 'repair-list',
        name: 'UserRepairList',
        component: () => import('@/views/user/RepairList.vue'),
        meta: { title: '报修记录' }
      },
      {
        // 评价信息页面
        path: 'evaluation',
        name: 'UserEvaluation',
        component: () => import('@/views/user/Evaluation.vue'),
        meta: { title: '评价信息' }
      },
      {
        // 个人信息页面
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/user/Profile.vue'),
        meta: { title: '个人信息' }
      },
      {
        // 留言板页面
        path: 'message-board',
        name: 'UserMessageBoard',
        component: () => import('@/views/user/MessageBoard.vue'),
        meta: { title: '留言板' }
      }
    ]
  },
  
  // ========== 维修人员模块 ==========
  {
    // 维修人员布局路由
    path: '/staff',
    name: 'StaffLayout',
    component: () => import('@/layouts/StaffLayout.vue'),
    redirect: '/staff/home',  // 默认重定向到工作台
    children: [
      {
        // 工作台首页
        path: 'home',
        name: 'StaffHome',
        component: () => import('@/views/staff/Home.vue'),
        meta: { title: '工作台' }
      },
      {
        // 报修接单页面
        path: 'accept',
        name: 'StaffAccept',
        component: () => import('@/views/staff/Accept.vue'),
        meta: { title: '报修接单' }
      },
      {
        // 我的工单列表
        path: 'my-orders',
        name: 'StaffMyOrders',
        component: () => import('@/views/staff/MyOrders.vue'),
        meta: { title: '我的工单' }
      },
      {
        // 设备报修处理页面
        path: 'repair-order',
        name: 'StaffRepairOrder',
        component: () => import('@/views/staff/RepairOrder.vue'),
        meta: { title: '设备报修' }
      },
      {
        // 维修记录页面
        path: 'record',
        name: 'StaffRecord',
        component: () => import('@/views/staff/Record.vue'),
        meta: { title: '维修记录' }
      },
      {
        // 设备巡检页面
        path: 'inspection',
        name: 'StaffInspection',
        component: () => import('@/views/staff/Inspection.vue'),
        meta: { title: '设备巡检' }
      },
      {
        // 维修知识库
        path: 'knowledge',
        name: 'StaffKnowledge',
        component: () => import('@/views/staff/Knowledge.vue'),
        meta: { title: '维修知识库' }
      },
      {
        // 评价信息页面
        path: 'evaluation',
        name: 'StaffEvaluation',
        component: () => import('@/views/staff/Evaluation.vue'),
        meta: { title: '评价信息' }
      },
      {
        // 个人信息页面
        path: 'profile',
        name: 'StaffProfile',
        component: () => import('@/views/staff/Profile.vue'),
        meta: { title: '个人信息' }
      }
    ]
  },
  
  // ========== 管理员模块 ==========
  {
    // 管理员布局路由
    path: '/admin',
    name: 'AdminLayout',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin/home',  // 默认重定向到管理员首页
    children: [
      {
        // 管理员首页
        path: 'home',
        name: 'AdminHome',
        component: () => import('@/views/admin/Home.vue'),
        meta: { title: '管理员首页' }
      },
      {
        // 统计分析页面
        path: 'statistics',
        name: 'AdminStatistics',
        component: () => import('@/views/admin/Statistics.vue'),
        meta: { title: '统计分析' }
      },
      {
        // 用户管理页面
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        // 维修人员管理页面
        path: 'staff',
        name: 'AdminStaff',
        component: () => import('@/views/admin/Staff.vue'),
        meta: { title: '维修员管理' }
      },
      {
        // 设备类型管理页面
        path: 'equipment-type',
        name: 'AdminEquipmentType',
        component: () => import('@/views/admin/EquipmentType.vue'),
        meta: { title: '设备类型' }
      },
      {
        // 校园位置管理页面
        path: 'location',
        name: 'AdminLocation',
        component: () => import('@/views/admin/LocationManage.vue'),
        meta: { title: '校园位置管理' }
      },
      {
        // 公共设备管理页面
        path: 'equipment',
        name: 'AdminEquipment',
        component: () => import('@/views/admin/Equipment.vue'),
        meta: { title: '公共设备' }
      },
      {
        // 设备报修管理页面
        path: 'repair-order',
        name: 'AdminRepairOrder',
        component: () => import('@/views/admin/RepairOrder.vue'),
        meta: { title: '设备报修' }
      },
      {
        // 维修记录管理页面
        path: 'record',
        name: 'AdminRecord',
        component: () => import('@/views/admin/Record.vue'),
        meta: { title: '维修记录' }
      },
      {
        // 备件库存管理页面
        path: 'spare-part',
        name: 'AdminSparePart',
        component: () => import('@/views/admin/SparePart.vue'),
        meta: { title: '备件库存' }
      },
      {
        // 维修知识库管理页面
        path: 'knowledge',
        name: 'AdminKnowledge',
        component: () => import('@/views/admin/Knowledge.vue'),
        meta: { title: '维修知识库' }
      },
      {
        // 评价信息管理页面
        path: 'evaluation',
        name: 'AdminEvaluation',
        component: () => import('@/views/admin/Evaluation.vue'),
        meta: { title: '评价信息' }
      },
      {
        // 设备巡检管理页面
        path: 'inspection',
        name: 'AdminInspection',
        component: () => import('@/views/admin/Inspection.vue'),
        meta: { title: '设备巡检' }
      },
      {
        // 校园公告管理页面
        path: 'announcement',
        name: 'AdminAnnouncement',
        component: () => import('@/views/admin/Announcement.vue'),
        meta: { title: '校园公告' }
      },
      {
        // 数据导出页面
        path: 'export',
        name: 'AdminExport',
        component: () => import('@/views/admin/Export.vue'),
        meta: { title: '数据导出' }
      },
      {
        // 个人信息页面
        path: 'profile',
        name: 'AdminProfile',
        component: () => import('@/views/admin/Profile.vue'),
        meta: { title: '个人信息' }
      },
      {
        // 留言管理页面
        path: 'message-board',
        name: 'AdminMessageBoard',
        component: () => import('@/views/admin/MessageBoard.vue'),
        meta: { title: '留言管理' }
      }
    ]
  }
]

/**
 * 创建路由实例
 * 
 * 使用HTML5 History模式，URL更美观（无#号）。
 * 需要服务器配置支持，所有路由都返回index.html。
 */
const router = createRouter({
  history: createWebHistory(),
  routes
})

/**
 * 全局前置路由守卫
 * 
 * 在每次路由跳转前执行，用于：
 * - 设置页面标题
 * - 可扩展：权限验证、登录检查等
 * 
 * @param {RouteLocationNormalized} to - 目标路由
 * @param {RouteLocationNormalized} from - 来源路由
 * @param {NavigationGuardNext} next - 放行函数
 */
router.beforeEach((to, from, next) => {
  document.title = to.meta.title 
    ? `${to.meta.title} - 佳木斯大学设备管理与报修系统` 
    : '佳木斯大学设备管理与报修系统'
  
  const publicPages = ['/', '/login', '/register']
  if (publicPages.includes(to.path)) {
    return next()
  }

  if (to.path.startsWith('/user/')) {
    if (!localStorage.getItem('userToken')) {
      return next('/login')
    }
  } else if (to.path.startsWith('/staff/')) {
    if (!localStorage.getItem('staffToken')) {
      return next('/login')
    }
  } else if (to.path.startsWith('/admin/')) {
    if (!localStorage.getItem('adminToken')) {
      return next('/login')
    }
  }
  
  next()
})

// 导出路由实例，供main.js使用
export default router
