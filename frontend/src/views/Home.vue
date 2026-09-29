<!--
  系统首页 - Home.vue
  
  该组件是系统的首页，面向所有访客，展示系统信息、校园公告和公共设备。
  主要功能：
  - 系统标题和登录入口
  - 轮播图展示
  - 校园公告列表和详情
  - 公共设施列表和搜索
  - 响应式设计
  
  组件结构：
  - template：包含头部、轮播图、公告、设施、页脚和公告详情弹窗
  - script：包含数据加载、搜索、公告查看等逻辑
  - style：包含首页的视觉样式
  
  作者：FMRS系统开发者-范广宇
  创建日期：2026年
-->

<template>
  <div class="home-page">
    <!-- 页面头部 -->
    <div class="header">
      <div class="logo">
        <h1>佳木斯大学设备管理与报修系统</h1>
      </div>
      <div class="nav">
        <el-button type="primary" @click="$router.push('/login')">登录</el-button>
      </div>
    </div>
    
    <!-- 轮播图区域 -->
    <div class="banner">
      <el-carousel height="450px" :interval="5000">
        <el-carousel-item>
          <div class="banner-item" style="background: url('/media/banner/campus1.jpg') center/cover no-repeat;">
            <div class="banner-overlay"></div>
            <div class="banner-content">
              <h2>佳木斯大学</h2>
              <p>华夏东极人才的摇篮</p>
            </div>
          </div>
        </el-carousel-item>
        <el-carousel-item>
          <div class="banner-item" style="background: url('/media/banner/campus2.jpg') center/cover no-repeat;">
            <div class="banner-overlay"></div>
            <div class="banner-content">
              <h2>快速报修</h2>
              <p>快速报修，及时维修，共建美好校园</p>
            </div>
          </div>
        </el-carousel-item>
        <el-carousel-item>
          <div class="banner-item" style="background: url('/media/banner/campus3.jpg') center/cover no-repeat;">
            <div class="banner-overlay"></div>
            <div class="banner-content">
              <h2>专业维修</h2>
              <p>专业维修团队，保障校园设施正常运行</p>
            </div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="content">
      <!-- 校园公告部分 -->
      <div class="section">
        <h2>校园公告</h2>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" v-for="item in announcements" :key="item.id">
            <el-card class="announcement-card" @click="handleViewAnnouncement(item)">
              <template #header>
                <span class="title">{{ item.title }}</span>
                <span class="time">{{ formatDate(item.publish_time) }}</span>
              </template>
              <p>{{ truncateContent(item.content) }}</p>
              <img v-if="item.image" :src="item.image" class="announcement-image" />
            </el-card>
          </el-col>
          <el-col :span="24" v-if="announcements.length === 0">
            <el-empty description="暂无公告" />
          </el-col>
        </el-row>
      </div>
      
      <!-- 公共设备部分 -->
      <div class="section">
        <h2>公共设备</h2>
        <div class="search-bar">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索设备名称"
            style="width: 300px;"
            @keyup.enter="searchEquipment"
            clearable
          >
            <template #append>
              <el-button icon="Search" @click="searchEquipment" />
            </template>
          </el-input>
        </div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="item in equipments" :key="item.id">
            <el-card class="equipment-card" shadow="hover" @click="handleViewEquipment(item)">
              <div class="equipment-image">
                <img v-if="item.equipment_image" :src="item.equipment_image" :alt="item.equipment_name" />
                <div v-else class="default-image">
                  <el-icon :size="40"><Monitor /></el-icon>
                </div>
              </div>
              <div class="info">
                <h3>{{ item.equipment_name }}</h3>
                <p class="info-row"><el-icon><Grid /></el-icon> {{ item.equipment_type_name || item.equipment_type_detail?.type_name || '未知' }}</p>
                <p v-if="item.location_info?.full_location && item.location_info.full_location !== '-'" class="info-row location-text"><el-icon><Location /></el-icon> {{ item.location_info.full_location }}</p>
                <p v-if="item.specification" class="info-row"><el-icon><Document /></el-icon> {{ item.specification }}</p>
                <p class="status-row">
                  <el-tag :type="getStatusType(item.status)" size="small">{{ item.status }}</el-tag>
                </p>
              </div>
            </el-card>
          </el-col>
          <el-col :span="24" v-if="equipments.length === 0 && !loadingEquipments">
            <el-empty description="暂无设备信息" />
          </el-col>
        </el-row>
        <div class="pagination-wrapper" v-if="equipmentTotal > equipmentPageSize">
          <el-pagination
            v-model:current-page="equipmentPage"
            :page-size="equipmentPageSize"
            :total="equipmentTotal"
            layout="total, prev, pager, next"
            @current-change="loadEquipments"
          />
        </div>
      </div>
    </div>
    
    <!-- 页脚 -->
    <div class="footer">
      <p>© 2026 佳木斯大学设施管理与报修系统 范广宇版权所有</p>
    </div>
    
    <!-- 公告详情弹窗 -->
    <el-dialog v-model="announcementVisible" :title="currentAnnouncement?.title || '公告详情'" width="700px" class="announcement-dialog">
      <div class="announcement-detail" v-if="currentAnnouncement">
        <div class="announcement-meta">
          <span class="publish-time">
            <el-icon><Clock /></el-icon>
            发布时间: {{ formatDate(currentAnnouncement.publish_time) }}
          </span>
        </div>
        <div class="announcement-content">
          <p>{{ currentAnnouncement.content || '暂无内容' }}</p>
        </div>
        <div class="announcement-image-wrapper" v-if="currentAnnouncement.image">
          <el-image
            :src="currentAnnouncement.image"
            :preview-src-list="[currentAnnouncement.image]"
            fit="contain"
            class="announcement-detail-image"
          />
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="announcementVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 设备详情弹窗 -->
    <el-dialog v-model="equipmentVisible" title="设备详情" width="780px">
      <div v-if="currentEquipment" class="equipment-detail">
        <div class="detail-header">
          <div v-if="currentEquipment.equipment_image" class="detail-image">
            <el-image :src="currentEquipment.equipment_image" fit="cover" :preview-src-list="[currentEquipment.equipment_image]" preview-teleported />
          </div>
          <div class="detail-title">
            <h3>{{ currentEquipment.equipment_name }}</h3>
            <span class="equipment-no">{{ currentEquipment.equipment_no }}</span>
          </div>
        </div>
        <div class="detail-content">
          <el-descriptions :column="2" border class="detail-descriptions">
            <el-descriptions-item label="设备类型" :span="1">
              {{ currentEquipment.equipment_type_detail?.type_name || currentEquipment.equipment_type_name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="所在位置" :span="1">
              {{ currentEquipment.location_info?.full_location || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="设备规格" :span="1">{{ currentEquipment.specification || '-' }}</el-descriptions-item>
            <el-descriptions-item label="供货商" :span="1">{{ currentEquipment.supplier || '-' }}</el-descriptions-item>
            <el-descriptions-item label="设备序号" :span="1">{{ currentEquipment.sequence_number }}</el-descriptions-item>
            <el-descriptions-item label="设备状态" :span="1">
              <el-tag :type="getStatusType(currentEquipment.status)">{{ currentEquipment.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="发布时间" :span="2">{{ formatDate(currentEquipment.publish_time) }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="equipmentVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 首页脚本
 * 
 * 使用Vue 3的组合式API（Composition API）编写。
 * 主要功能：
 * - 加载校园公告列表
 * - 加载公共设施列表
 * - 搜索公共设施
 * - 查看公告详情
 * - 日期格式化
 * - 内容截断
 */
import { ref, onMounted } from 'vue'
import { announcementApi, equipmentApi } from '@/api'
import { Clock, Monitor, Grid, Location, Document } from '@element-plus/icons-vue'

/**
 * 搜索关键词
 * @type {Ref<string>}
 */
const searchKeyword = ref('')

/**
 * 公告列表
 * @type {Ref<Array>}
 */
const announcements = ref([])

/**
 * 设备列表
 * @type {Ref<Array>}
 */
const equipments = ref([])
const equipmentPage = ref(1)
const equipmentPageSize = ref(24)
const equipmentTotal = ref(0)
const loadingEquipments = ref(false)

/**
 * 公告详情弹窗可见性
 * @type {Ref<boolean>}
 */
const announcementVisible = ref(false)

/**
 * 当前查看的公告
 * @type {Ref<Object>}
 */
const currentAnnouncement = ref(null)

/**
 * 设备详情弹窗可见性
 * @type {Ref<boolean>}
 */
const equipmentVisible = ref(false)

/**
 * 当前查看的设备
 * @type {Ref<Object>}
 */
const currentEquipment = ref(null)

/**
 * 查看设备详情
 * @param {Object} item - 设备对象
 */
const handleViewEquipment = (item) => {
  currentEquipment.value = item
  equipmentVisible.value = true
}

/**
 * 根据设备状态获取标签类型
 * @param {string} status - 设备状态
 * @returns {string} 标签类型
 */
const getStatusType = (status) => {
  if (status === '正常') return 'success'
  if (status === '故障') return 'danger'
  if (String(status).includes('故障')) return 'warning'
  return 'info'
}

/**
 * 组件挂载时加载数据
 * @async
 * @returns {Promise<void>}
 */
onMounted(async () => {
  await loadAnnouncements()
  await loadEquipments()
})

/**
 * 加载公告列表
 * @async
 * @returns {Promise<void>}
 */
const loadAnnouncements = async () => {
  try {
    const res = await announcementApi.list({ page_size: 4 })
    if (res.results) {
      announcements.value = res.results
    }
  } catch (error) {
    console.error('加载公告失败:', error)
  }
}

/**
 * 加载设备列表
 * @async
 * @returns {Promise<void>}
 */
const loadEquipments = async () => {
  loadingEquipments.value = true
  try {
    const params = { page: equipmentPage.value, page_size: equipmentPageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    const res = await equipmentApi.list(params)
    if (res.results) {
      equipments.value = res.results
      equipmentTotal.value = res.count || 0
    }
  } catch (error) {
    console.error('加载设备失败:', error)
  } finally {
    loadingEquipments.value = false
  }
}

/**
 * 搜索设备
 * @async
 * @returns {Promise<void>}
 */
const searchEquipment = async () => {
  equipmentPage.value = 1
  await loadEquipments()
}

/**
 * 查看公告详情
 * @param {Object} item - 公告对象
 */
const handleViewAnnouncement = (item) => {
  currentAnnouncement.value = item
  announcementVisible.value = true
}

/**
 * 截断内容
 * @param {string} content - 原始内容
 * @returns {string} 截断后的内容
 */
const truncateContent = (content) => {
  if (!content) return '暂无内容'
  if (content.length > 80) {
    return content.substring(0, 80) + '...'
  }
  return content
}

/**
 * 格式化日期
 * @param {string} dateStr - 日期字符串
 * @returns {string} 格式化后的日期
 */
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped lang="scss">
/**
 * 首页样式
 * 
 * 采用深蓝渐变头部，响应式设计，卡片悬浮效果。
 * 包含：
 * - 响应式布局
 * - 轮播图样式
 * - 公告卡片样式
 * - 设备卡片样式
 * - 页脚样式
 */
.home-page {
  min-height: 100vh;
  background: var(--gray-50);
  
  .header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #1e40af 100%);
    padding: 0 50px;
    height: 64px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
    
    h1 {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.5px;
      
      @media (max-width: 768px) {
        font-size: 16px;
      }
    }
    
    :deep(.el-button--primary) {
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.3);
      border-radius: var(--radius-lg);
      backdrop-filter: blur(10px);
      font-weight: 500;
      transition: all var(--transition-normal);
      
      &:hover {
        background: rgba(255, 255, 255, 0.25);
        border-color: rgba(255, 255, 255, 0.5);
        transform: translateY(-1px);
      }
    }
    
    @media (max-width: 768px) {
      padding: 0 15px;
    }
  }
  
  .banner {
    .banner-item {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }
    
    .banner-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(180deg, rgba(0, 0, 0, 0.1) 0%, rgba(0, 0, 0, 0.4) 100%);
    }
    
    .banner-content {
      position: relative;
      text-align: center;
      color: #fff;
      text-shadow: 0 2px 8px rgba(0,0,0,0.3);
      padding: 20px;
      z-index: 1;
      
      h2 {
        font-size: 44px;
        margin-bottom: 16px;
        font-weight: 800;
        letter-spacing: 2px;
        
        @media (max-width: 768px) {
          font-size: 28px;
        }
      }
      
      p {
        font-size: 18px;
        font-weight: 300;
        letter-spacing: 1px;
        
        @media (max-width: 768px) {
          font-size: 15px;
        }
      }
    }
  }
  
  .content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 48px 20px;
    
    @media (max-width: 768px) {
      padding: 24px 15px;
    }
    
    .section {
      margin-bottom: 48px;
      
      h2 {
        font-size: 24px;
        margin-bottom: 24px;
        padding-left: 14px;
        border-left: 4px solid #1e40af;
        font-weight: 700;
        color: var(--gray-800);
        letter-spacing: -0.3px;
        
        @media (max-width: 768px) {
          font-size: 20px;
        }
      }
    }
    
    .search-bar {
      margin-bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      
      @media (max-width: 768px) {
        .el-input {
          width: 100% !important;
        }
      }
    }
  }
  
  .announcement-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: all var(--transition-normal);
    border-radius: var(--radius-lg) !important;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg) !important;
    }
    
    :deep(.el-card__header) {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 18px;
      
      .title {
        font-weight: 600;
        color: var(--gray-800);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex: 1;
      }
      
      .time {
        color: var(--gray-400);
        font-size: 12px;
        margin-left: 10px;
        flex-shrink: 0;
      }
    }
    
    p {
      color: var(--gray-500);
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      margin: 0;
      line-height: 1.6;
    }
    
    .announcement-image {
      width: 100%;
      max-height: 200px;
      object-fit: cover;
      margin-top: 10px;
      border-radius: var(--radius-md);
    }
  }
  
  .equipment-card {
    margin-bottom: 16px;
    cursor: pointer;
    transition: all var(--transition-normal);
    border-radius: var(--radius-lg) !important;
    overflow: hidden;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg) !important;
    }
    
    .equipment-image {
      width: 100%;
      height: 130px;
      overflow: hidden;
      background: linear-gradient(135deg, var(--gray-50), var(--gray-100));
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform var(--transition-slow);
      }
      
      .default-image {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--gray-300);
      }
    }
    
    &:hover .equipment-image img {
      transform: scale(1.05);
    }
    
    .info {
      padding: 10px 0;
      
      h3 {
        font-size: 14px;
        margin-bottom: 6px;
        font-weight: 600;
        color: var(--gray-800);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .info-row {
        font-size: 12px;
        color: var(--gray-500);
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .location-text {
        color: var(--gray-600);
      }
      
      .status-row {
        margin-top: 4px;
        margin-bottom: 0;
      }
    }
  }
  
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
  
  .footer {
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    color: rgba(255, 255, 255, 0.7);
    text-align: center;
    padding: 24px;
    font-size: 13px;
    
    p {
      margin: 0;
    }
  }
}

.announcement-detail {
  .announcement-meta {
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--gray-100);

    .publish-time {
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--gray-500);
      font-size: 14px;
    }
  }

  .announcement-content {
    font-size: 15px;
    line-height: 1.8;
    color: var(--gray-700);
    margin-bottom: 20px;

    p {
      white-space: pre-wrap;
    }
  }

  .announcement-image-wrapper {
    text-align: center;

    .announcement-detail-image {
      max-width: 100%;
      max-height: 400px;
      border-radius: var(--radius-lg);
    }
  }
}

.equipment-detail {
  .detail-header {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #ebeef5;
  }
  .detail-image {
    width: 120px;
    height: 120px;
    border-radius: 8px;
    overflow: hidden;
    flex-shrink: 0;
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  .detail-title {
    flex: 1;
    h3 {
      font-size: 18px;
      font-weight: 600;
      margin: 0 0 8px 0;
      color: #1f2329;
    }
    .equipment-no {
      font-size: 13px;
      color: #8f959e;
    }
  }
  .detail-content {
    .detail-descriptions {
      :deep(.el-descriptions__label) {
        color: #646a73;
        font-weight: 500;
        min-width: 80px;
        text-align: left;
      }
      :deep(.el-descriptions__content) {
        color: #1f2329;
      }
    }
  }
}
</style>
