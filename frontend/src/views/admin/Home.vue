<template>
  <div class="admin-home">
    <div class="page-header">
      <h2>系统首页</h2>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.userCount }}</div>
            <div class="stat-label">注册用户</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.equipmentCount }}</div>
            <div class="stat-label">已录入设备</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon><Tools /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.repairCount }}</div>
            <div class="stat-label">报修总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #f56c6c;">
            <el-icon><Avatar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.staffCount }}</div>
            <div class="stat-label">维修员</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>设备类型分布</span>
          </template>
          <div ref="equipmentChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>报修状态统计</span>
          </template>
          <div ref="repairChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>校园公告</span>
      </template>
      <el-table :data="announcements" stripe>
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="publisher" label="发布人" width="120" />
        <el-table-column prop="publish_time" label="发布时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { userApi, equipmentApi, repairApi, announcementApi, staffApi } from '@/api'

const stats = ref({
  userCount: 0,
  equipmentCount: 0,
  repairCount: 0,
  staffCount: 0
})

const announcements = ref([])
const equipmentChart = ref()
const repairChart = ref()
let equipmentChartInstance = null
let repairChartInstance = null

onMounted(async () => {
  await Promise.all([loadDashboard(), loadAnnouncements()])
})

onUnmounted(() => {
  equipmentChartInstance?.dispose()
  repairChartInstance?.dispose()
})

const loadDashboard = async () => {
  try {
    const [statRes, userRes, equipRes, staffRes, typeRes] = await Promise.all([
      repairApi.orderStatistics(),
      userApi.list({ page_size: 1 }),
      equipmentApi.list({ page_size: 1 }),
      staffApi.list({ page_size: 1 }),
      equipmentApi.typeList({ page_size: 100 })
    ])

    stats.value = {
      userCount: userRes.count || 0,
      equipmentCount: equipRes.count || 0,
      repairCount: statRes.total || 0,
      staffCount: staffRes.count || 0
    }

    equipmentChartInstance = echarts.init(equipmentChart.value)
    repairChartInstance = echarts.init(repairChart.value)

    const types = typeRes.results || []
    const chartData = types.filter(t => (t.equipment_count || 0) > 0).map(t => ({ name: t.type_name, value: t.equipment_count }))
    equipmentChartInstance.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c}' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{ name: '设备类型', type: 'pie', radius: '50%', data: chartData }]
    })

    repairChartInstance.setOption({
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left' },
      series: [{
        name: '报修状态',
        type: 'pie',
        radius: '50%',
        data: [
          { name: '待接单', value: statRes.pending || 0 },
          { name: '维修中', value: statRes.accepted || 0 },
          { name: '待审核', value: statRes.repairing || 0 },
          { name: '已完成', value: statRes.completed || 0 }
        ]
      }]
    })
  } catch (error) {
    console.error(error)
  }
}

const loadAnnouncements = async () => {
  try {
    const res = await announcementApi.list({ page_size: 5 })
    announcements.value = res.results || []
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped lang="scss">
.admin-home {
  animation: fadeIn 0.3s ease;
  
  .stat-card {
    display: flex;
    align-items: center;
    padding: 24px;
    border-radius: var(--radius-xl) !important;
    transition: all var(--transition-normal);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg) !important;
    }
    
    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: var(--radius-lg);
      display: flex;
      justify-content: center;
      align-items: center;
      color: #fff;
      font-size: 26px;
      flex-shrink: 0;
    }
    
    .stat-info {
      margin-left: 18px;
      
      .stat-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--gray-800);
        letter-spacing: -0.5px;
      }
      
      .stat-label {
        color: var(--gray-500);
        margin-top: 4px;
        font-size: 13px;
        font-weight: 500;
      }
    }
  }
  
  :deep(.el-card) {
    border-radius: var(--radius-xl) !important;
  }
}
</style>
