<template>
  <div class="statistics-page">
    <div class="page-header"><h2>统计分析</h2></div>
    
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <el-icon><Tools /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalOrders }}</div>
            <div class="stat-label">报修总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingOrders }}</div>
            <div class="stat-label">待处理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <el-icon><Setting /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.processingOrders }}</div>
            <div class="stat-label">处理中</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.completedOrders }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="6">
        <el-card class="stat-card small">
          <div class="stat-info">
            <div class="stat-value" style="color: #e6a23c;">{{ stats.avgDuration }}</div>
            <div class="stat-label">平均维修时长(小时)</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card small">
          <div class="stat-info">
            <div class="stat-value" style="color: #67c23a;">{{ stats.completionRate }}%</div>
            <div class="stat-label">完成率</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card small">
          <div class="stat-info">
            <div class="stat-value" style="color: #409eff;">{{ stats.avgRating }}</div>
            <div class="stat-label">平均评分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card small">
          <div class="stat-info">
            <div class="stat-value" style="color: #f56c6c;">{{ stats.urgentOrders }}</div>
            <div class="stat-label">紧急工单</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>报修趋势（近7天）</span>
              <el-radio-group v-model="trendRange" size="small">
                <el-radio-button label="7">近7天</el-radio-button>
                <el-radio-button label="30">近30天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>设备类型分布</span>
          </template>
          <div ref="typeChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>工单状态分布</span>
          </template>
          <div ref="statusChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>维修员工作量排名</span>
          </template>
          <div ref="staffChart" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>校区报修统计</span>
            </div>
          </template>
          <div ref="campusChart" style="height: 250px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>热门报修设备TOP10</span>
          </template>
          <el-table :data="hotEquipments" stripe size="small">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="equipment_name" label="设备名称" />
            <el-table-column prop="repair_count" label="报修次数" width="100" />
            <el-table-column prop="location" label="位置" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>紧急工单（教师报修未审核完成）</span>
          </template>
          <el-table :data="urgentOrderList" stripe size="small" v-loading="urgentLoading">
            <el-table-column prop="repair_no" label="报修编号" width="140" />
            <el-table-column prop="equipment_name" label="设备名称" />
            <el-table-column prop="user_name" label="报修人" width="80" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="报修时间" width="150">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!urgentLoading && urgentOrderList.length === 0" description="暂无紧急工单" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { repairApi, equipmentApi } from '@/api'
import { Tools, Clock, Setting, CircleCheck } from '@element-plus/icons-vue'
import { EventBus, Events } from '@/utils/eventBus'

const stats = ref({
  totalOrders: 0,
  pendingOrders: 0,
  processingOrders: 0,
  completedOrders: 0,
  avgDuration: 0,
  completionRate: 0,
  avgRating: 0,
  urgentOrders: 0
})

const trendRange = ref('7')
const hotEquipments = ref([])
const urgentOrderList = ref([])
const urgentLoading = ref(false)

const trendChart = ref()
const typeChart = ref()
const statusChart = ref()
const staffChart = ref()
const campusChart = ref()

let trendChartInstance = null
let typeChartInstance = null
let statusChartInstance = null
let staffChartInstance = null
let campusChartInstance = null

let cachedDashboard = null

onMounted(async () => {
  initChartInstances()
  await loadDashboard()
  
  window.addEventListener('resize', handleResize)
  EventBus.on(Events.RECORD_DELETED, handleDataRefresh)
  EventBus.on(Events.DATA_REFRESH, handleDataRefresh)
})

const initChartInstances = () => {
  trendChartInstance = echarts.init(trendChart.value)
  typeChartInstance = echarts.init(typeChart.value)
  statusChartInstance = echarts.init(statusChart.value)
  staffChartInstance = echarts.init(staffChart.value)
  campusChartInstance = echarts.init(campusChart.value)
}

const handleResize = () => {
  trendChartInstance?.resize()
  typeChartInstance?.resize()
  statusChartInstance?.resize()
  staffChartInstance?.resize()
  campusChartInstance?.resize()
}

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChartInstance?.dispose()
  typeChartInstance?.dispose()
  statusChartInstance?.dispose()
  staffChartInstance?.dispose()
  campusChartInstance?.dispose()
  
  EventBus.off(Events.RECORD_DELETED, handleDataRefresh)
  EventBus.off(Events.DATA_REFRESH, handleDataRefresh)
})

const handleDataRefresh = () => {
  cachedDashboard = null
  loadDashboard()
}

watch(trendRange, () => {
  if (cachedDashboard) {
    renderTrendChart(cachedDashboard.trend || [])
  } else {
    loadTrendOnly()
  }
})

const loadDashboard = async () => {
  urgentLoading.value = true
  try {
    const [dashRes, equipStatRes] = await Promise.all([
      repairApi.orderStatistics({ trend_days: 30 }),
      equipmentApi.typeStatistics().catch(() => ({}))
    ])

    cachedDashboard = dashRes

    stats.value = {
      totalOrders: dashRes.total || 0,
      pendingOrders: dashRes.pending || 0,
      processingOrders: dashRes.accepted || 0,
      completedOrders: dashRes.completed || 0,
      avgDuration: dashRes.avg_duration || 0,
      completionRate: dashRes.completion_rate || 0,
      avgRating: dashRes.avg_rating || 0,
      urgentOrders: dashRes.urgent_orders || 0
    }

    hotEquipments.value = dashRes.hot_equipments || []
    urgentOrderList.value = (dashRes.urgent_orders_list || []).map(o => ({
      ...o,
      created_at: o.created_at ? new Date(o.created_at).toLocaleString('zh-CN') : ''
    }))

    renderTrendChart(dashRes.trend || [])
    renderTypeChart(equipStatRes.type_stats || [])
    renderStatusChart()
    renderStaffChart(dashRes.staff_completed || [])
    renderCampusChart(dashRes.campus_distribution || {})
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    urgentLoading.value = false
  }
}

const loadTrendOnly = async () => {
  try {
    const dashRes = await repairApi.orderStatistics({ trend_days: 30 })
    cachedDashboard = dashRes
    renderTrendChart(dashRes.trend || [])
  } catch (error) {
    console.error(error)
  }
}

const renderTrendChart = (trendData) => {
  if (!trendChartInstance) return
  const days = parseInt(trendRange.value)
  const data = trendData.slice(-days)
  trendChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['报修数', '完成数'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: data.map(d => d.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '报修数', type: 'line', smooth: true, data: data.map(d => d.total), areaStyle: { opacity: 0.3 } },
      { name: '完成数', type: 'line', smooth: true, data: data.map(d => d.completed), areaStyle: { opacity: 0.3 } }
    ]
  })
}

const renderTypeChart = (typeStats) => {
  if (!typeChartInstance) return
  const chartData = typeStats
    .filter(s => (s.equipment_count || 0) > 0)
    .map(s => ({ name: s.type_name, value: s.equipment_count }))
    .sort((a, b) => b.value - a.value)
  typeChartInstance.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      name: '设备类型', type: 'pie', radius: ['40%', '70%'], center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: chartData
    }]
  })
}

const renderStatusChart = () => {
  if (!statusChartInstance) return
  statusChartInstance.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: '5%', left: 'center' },
    series: [{
      name: '工单状态', type: 'pie', radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {c}' },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [
        { value: stats.value.pendingOrders, name: '待处理', itemStyle: { color: '#e6a23c' } },
        { value: stats.value.processingOrders, name: '处理中', itemStyle: { color: '#409eff' } },
        { value: stats.value.completedOrders, name: '已完成', itemStyle: { color: '#67c23a' } }
      ]
    }]
  })
}

const renderStaffChart = (staffData) => {
  if (!staffChartInstance) return
  const chartData = staffData.filter(s => s.count > 0).sort((a, b) => a.count - b.count).slice(-10)
  staffChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: chartData.map(s => s.name) },
    series: [{
      name: '完成工单数', type: 'bar', data: chartData.map(s => s.count),
      itemStyle: { borderRadius: [0, 4, 4, 0], color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
        { offset: 0, color: '#83bff6' },
        { offset: 0.5, color: '#188df0' },
        { offset: 1, color: '#188df0' }
      ])}
    }]
  })
}

const renderCampusChart = (campusData) => {
  if (!campusChartInstance) return
  const labels = Object.keys(campusData)
  const values = Object.values(campusData)
  campusChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series: [{
      name: '报修数', type: 'bar', data: values,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: '#83bff6' },
        { offset: 1, color: '#188df0' }
      ])}
    }]
  })
}

const getStatusType = (s) => ({ WAITING: 'warning', IN_PROGRESS: 'primary', PENDING_ADMIN_CLOSE: 'info', CLOSED: 'success', REJECTED: 'danger' })[s] || 'info'
const getStatusText = (s) => ({ WAITING: '待接单', IN_PROGRESS: '维修中', PENDING_ADMIN_CLOSE: '待审核', CLOSED: '已完成', REJECTED: '已驳回' })[s] || s
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''
</script>

<style scoped lang="scss">
.statistics-page {
  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    
    &.small {
      justify-content: center;
      padding: 15px;
    }
    
    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      justify-content: center;
      align-items: center;
      color: #fff;
      font-size: 28px;
    }
    
    .stat-info {
      margin-left: 20px;
      
      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
      }
      
      .stat-label {
        color: #909399;
        margin-top: 5px;
        font-size: 14px;
      }
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
