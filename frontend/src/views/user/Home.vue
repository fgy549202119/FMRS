<template>
  <div class="user-home">
    <div class="page-header">
      <h2>个人中心</h2>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="user-card">
          <div class="user-info">
            <el-avatar :src="userInfo.avatar || defaultAvatar" :size="80" />
            <h3>{{ userInfo.real_name }}</h3>
            <p>{{ getUserType(userInfo.user_type) }}</p>
          </div>
          <div class="user-stats">
            <div class="stat-row">
              <span class="label">报修次数</span>
              <span class="value">{{ stats.total }}</span>
            </div>
            <div class="stat-row">
              <span class="label">待处理</span>
              <span class="value warning">{{ stats.pending }}</span>
            </div>
            <div class="stat-row">
              <span class="label">已完成</span>
              <span class="value success">{{ stats.completed }}</span>
            </div>
          </div>
          <el-button type="primary" class="edit-btn" @click="router.push('/user/profile')">
            <el-icon><Edit /></el-icon> 编辑资料
          </el-button>
        </el-card>
      </el-col>
      
      <el-col :span="18">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>报修统计</span>
              <el-radio-group v-model="chartRange" size="small">
                <el-radio-button label="week">本周</el-radio-button>
                <el-radio-button label="month">本月</el-radio-button>
                <el-radio-button label="year">本年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="stats-grid">
            <div class="stat-box">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.total }}</div>
                <div class="stat-label">总报修数</div>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.pending }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <el-icon><Setting /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.processing }}</div>
                <div class="stat-label">处理中</div>
              </div>
            </div>
            <div class="stat-box">
              <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ stats.completed }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
          </div>
        </el-card>
        
        <el-card style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>最近报修记录</span>
              <el-button type="primary" link @click="router.push('/user/repair-list')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentRepairs" stripe>
            <el-table-column prop="repair_no" label="报修编号" width="150" />
            <el-table-column prop="equipment_name" label="设备名称" />
            <el-table-column prop="location" label="位置" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="报修时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewDetail(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <el-dialog v-model="detailVisible" title="报修详情" width="600px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="报修编号">{{ currentOrder.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">{{ getStatusText(currentOrder.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentOrder.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentOrder.equipment_type_name || (isNaN(currentOrder.equipment_type) ? currentOrder.equipment_type : '-') }}</el-descriptions-item>
        <el-descriptions-item label="设备位置" :span="2">{{ currentOrder.location }}</el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentOrder.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="接单时间" v-if="currentOrder.accept_time">{{ formatDate(currentOrder.accept_time) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userApi, repairApi } from '@/api'
import { Document, Clock, Setting, CircleCheck, Edit } from '@element-plus/icons-vue'

const router = useRouter()
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
const userInfo = ref({})
const stats = ref({ total: 0, pending: 0, processing: 0, completed: 0 })
const recentRepairs = ref([])
const chartRange = ref('week')
const detailVisible = ref(false)
const currentOrder = ref(null)

onMounted(async () => {
  await Promise.all([loadUserInfo(), loadStats(), loadRecentRepairs()])
})

const loadUserInfo = async () => {
  try {
    const res = await userApi.profile()
    if (res.code === 200) {
      userInfo.value = res.data
    }
  } catch (error) {
    console.error(error)
  }
}

const loadStats = async () => {
  try {
    const res = await repairApi.orderStatistics()
    stats.value = {
      total: res.total || 0,
      pending: res.pending || 0,
      processing: res.accepted || 0,
      completed: res.completed || 0
    }
  } catch (error) {
    console.error(error)
  }
}

const loadRecentRepairs = async () => {
  try {
    const res = await repairApi.orderList({ page_size: 5 })
    recentRepairs.value = res.results || []
  } catch (error) {
    console.error(error)
  }
}

const viewDetail = (row) => {
  currentOrder.value = row
  detailVisible.value = true
}

const getUserType = (type) => {
  const types = { student: '学生', teacher: '教师', staff: '维修员', admin: '管理员' }
  return types[type] || '用户'
}

const getStatusType = (status) => {
  const map = {
    WAITING: 'warning',
    IN_PROGRESS: 'primary',
    PENDING_ADMIN_CLOSE: 'info',
    CLOSED: 'success',
    REJECTED: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    WAITING: '待接单',
    IN_PROGRESS: '处理中',
    PENDING_ADMIN_CLOSE: '待验收',
    CLOSED: '已完成',
    REJECTED: '已取消'
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped lang="scss">
.user-home {
  .user-card {
    .user-info {
      text-align: center;
      padding: 20px 0;
      border-bottom: 1px solid #eee;
      
      h3 {
        margin: 10px 0 5px;
        font-size: 18px;
      }
      
      p {
        color: #666;
        font-size: 14px;
      }
    }
    
    .user-stats {
      padding: 15px 20px;
      
      .stat-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px dashed #eee;
        
        &:last-child {
          border-bottom: none;
        }
        
        .label {
          color: #666;
        }
        
        .value {
          font-weight: bold;
          
          &.warning { color: #e6a23c; }
          &.success { color: #67c23a; }
        }
      }
    }
    
    .edit-btn {
      width: calc(100% - 40px);
      margin: 15px 20px;
    }
  }
  
  .chart-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      
      .stat-box {
        display: flex;
        align-items: center;
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
        
        .stat-icon {
          width: 50px;
          height: 50px;
          border-radius: 10px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
          font-size: 24px;
          margin-right: 15px;
        }
        
        .stat-content {
          .stat-number {
            font-size: 28px;
            font-weight: bold;
            color: #303133;
          }
          
          .stat-label {
            color: #909399;
            font-size: 14px;
          }
        }
      }
    }
  }
}
</style>
