<template>
  <div class="page">
    <div class="page-header"><h2>评价管理</h2></div>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value">{{ overview.total_count }}</div>
          <div class="stat-label">总评价数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value rating">{{ overview.avg_rating }}</div>
          <div class="stat-label">平均星级</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value appeal">{{ pendingAppealCount }}</div>
          <div class="stat-label">待处理申诉</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>评价列表</span>
          <div class="header-actions">
            <el-select v-model="filterRating" placeholder="评分筛选" clearable style="width: 120px; margin-right: 10px;" @change="loadEvaluations">
              <el-option label="5星" :value="5" />
              <el-option label="4星" :value="4" />
              <el-option label="3星" :value="3" />
              <el-option label="2星" :value="2" />
              <el-option label="1星" :value="1" />
            </el-select>
          </div>
        </div>
      </template>
      <el-table :data="evaluations" stripe v-loading="loading">
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="user_name" label="评价人" width="100" />
        <el-table-column prop="staff_name" label="维修员" width="100" />
        <el-table-column label="评分" width="120">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评价内容" show-overflow-tooltip />
        <el-table-column label="评价状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_hidden && row.appeal_status === 'approved'" type="warning">待评价</el-tag>
            <el-tag v-else-if="row.appeal_status === 'pending'" type="info">申诉中</el-tag>
            <el-tag v-else-if="row.appeal_status === 'rejected'" type="danger">已驳回</el-tag>
            <el-tag v-else type="success">已评价</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="评价时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">查看</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @current-change="loadEvaluations"
        @size-change="loadEvaluations"
        style="margin-top: 15px; justify-content: flex-end;"
      />
    </el-card>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header><span>维修员星级排行</span></template>
          <div ref="rankingChart" class="chart-container-lg"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>评价月度趋势</span></template>
          <div ref="trendChart" class="chart-container-lg"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card>
          <template #header><span>维修质量评分分布</span></template>
          <div ref="qualityChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span>响应速度评分分布</span></template>
          <div ref="speedChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header><span>服务态度评分分布</span></template>
          <div ref="attitudeChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>申诉管理</span>
          <el-radio-group v-model="appealStatus" size="small" @change="loadAppeals">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="pending">待处理</el-radio-button>
            <el-radio-button label="approved">已通过</el-radio-button>
            <el-radio-button label="rejected">已驳回</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table :data="appeals" stripe>
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="staff_name" label="申诉人" width="100" />
        <el-table-column label="原评价" width="150">
          <template #default="{ row }">
            <div v-if="row.evaluation_detail">
              <el-tag :type="getRatingType(row.evaluation_detail.rating)">{{ row.evaluation_detail.rating }}星</el-tag>
              <div style="font-size: 12px; color: #666; margin-top: 5px;">{{ row.evaluation_detail.content || '无内容' }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="申诉理由" />
        <el-table-column label="证据照片" width="80">
          <template #default="{ row }">
            <el-image v-if="row.evidence" :src="row.evidence" style="width: 50px; height: 50px;" fit="cover" :preview-src-list="[row.evidence]" preview-teleported />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getAppealStatusType(row.status)">{{ getAppealStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申诉时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button type="success" link size="small" @click="approveAppeal(row)">通过</el-button>
              <el-button type="danger" link size="small" @click="rejectAppeal(row)">驳回</el-button>
            </template>
            <span v-else style="color: #999;">已处理</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="detailVisible" title="评价详情" width="500px">
      <div v-if="currentEvaluation" class="evaluation-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报修编号">{{ currentEvaluation.repair_no }}</el-descriptions-item>
          <el-descriptions-item label="评价人">{{ currentEvaluation.user_name }}</el-descriptions-item>
          <el-descriptions-item label="维修员">{{ currentEvaluation.staff_name }}</el-descriptions-item>
          <el-descriptions-item label="评价状态">
            <el-tag v-if="currentEvaluation.is_hidden && currentEvaluation.appeal_status === 'approved'" type="warning">待评价</el-tag>
            <el-tag v-else-if="currentEvaluation.appeal_status === 'pending'" type="info">申诉中</el-tag>
            <el-tag v-else-if="currentEvaluation.appeal_status === 'rejected'" type="danger">已驳回</el-tag>
            <el-tag v-else type="success">已评价</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="维修质量">{{ currentEvaluation.quality_rating }}星</el-descriptions-item>
          <el-descriptions-item label="响应速度">{{ currentEvaluation.speed_rating }}星</el-descriptions-item>
          <el-descriptions-item label="服务态度">{{ currentEvaluation.attitude_rating }}星</el-descriptions-item>
          <el-descriptions-item label="综合评分">{{ currentEvaluation.rating }}星</el-descriptions-item>
          <el-descriptions-item label="评价内容" :span="2">{{ currentEvaluation.content || '无' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
    
    <el-dialog v-model="handleAppealVisible" :title="handleAppealType === 'approve' ? '通过申诉' : '驳回申诉'" width="400px">
      <el-input v-model="handleReply" type="textarea" :rows="3" placeholder="请输入处理意见" />
      <template #footer>
        <el-button @click="handleAppealVisible = false">取消</el-button>
        <el-button :type="handleAppealType === 'approve' ? 'success' : 'danger'" @click="submitHandleAppeal" :loading="handling">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { evaluationApi, appealApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { EventBus, Events } from '@/utils/eventBus'

const overview = ref({ total_count: 0, avg_rating: 0 })
const appeals = ref([])
const appealStatus = ref('')
const pendingAppealCount = ref(0)

const loading = ref(false)
const evaluations = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterRating = ref(null)

const detailVisible = ref(false)
const currentEvaluation = ref(null)

const handleAppealVisible = ref(false)
const handleAppealType = ref('')
const handleReply = ref('')
const handling = ref(false)
const currentAppeal = ref(null)

const rankingChart = ref()
const trendChart = ref()
const qualityChart = ref()
const speedChart = ref()
const attitudeChart = ref()

let rankingChartInstance = null
let trendChartInstance = null
let qualityChartInstance = null
let speedChartInstance = null
let attitudeChartInstance = null

onMounted(async () => {
  await loadOverview()
  await loadEvaluations()
  await loadAppeals()
  initCharts()
  
  EventBus.on(Events.RECORD_DELETED, handleRecordDeleted)
  EventBus.on(Events.DATA_REFRESH, handleDataRefresh)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  rankingChartInstance?.dispose()
  trendChartInstance?.dispose()
  qualityChartInstance?.dispose()
  speedChartInstance?.dispose()
  attitudeChartInstance?.dispose()
  
  EventBus.off(Events.RECORD_DELETED, handleRecordDeleted)
  EventBus.off(Events.DATA_REFRESH, handleDataRefresh)
})

const handleRecordDeleted = async () => {
  await loadOverview()
  await loadEvaluations()
  await updateRankingChart()
  await updateTrendChart()
  await updateDimensionCharts()
}

const handleDataRefresh = async () => {
  await loadOverview()
  await loadEvaluations()
  await loadAppeals()
  await updateRankingChart()
  await updateTrendChart()
  await updateDimensionCharts()
}

const loadOverview = async () => {
  try {
    const res = await evaluationApi.statistics()
    overview.value = res
  } catch (error) {
    console.error(error)
  }
}

const loadEvaluations = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (filterRating.value) params.rating = filterRating.value
    const res = await evaluationApi.list(params)
    evaluations.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除该评价？此操作不可恢复！', '提示', { type: 'warning' })
    await evaluationApi.delete(row.id)
    ElMessage.success('删除成功')
    EventBus.emit(Events.DATA_REFRESH)
    loadEvaluations()
    loadOverview()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const loadAppeals = async () => {
  try {
    const params = {}
    if (appealStatus.value) {
      params.status = appealStatus.value
    }
    const res = await appealApi.list(params)
    appeals.value = res.results || res
    pendingAppealCount.value = (res.results || res).filter(a => a.status === 'pending').length
  } catch (error) {
    console.error(error)
  }
}

const initCharts = async () => {
  await nextTick()

  if (rankingChart.value) {
    rankingChartInstance = echarts.init(rankingChart.value)
  }
  if (trendChart.value) {
    trendChartInstance = echarts.init(trendChart.value)
  }
  if (qualityChart.value) {
    qualityChartInstance = echarts.init(qualityChart.value)
  }
  if (speedChart.value) {
    speedChartInstance = echarts.init(speedChart.value)
  }
  if (attitudeChart.value) {
    attitudeChartInstance = echarts.init(attitudeChart.value)
  }

  window.addEventListener('resize', handleResize)

  await updateRankingChart()
  await updateTrendChart()
  await updateDimensionCharts()
}

const handleResize = () => {
  rankingChartInstance?.resize()
  trendChartInstance?.resize()
  qualityChartInstance?.resize()
  speedChartInstance?.resize()
  attitudeChartInstance?.resize()
}

const updateRankingChart = async () => {
  try {
    const res = await evaluationApi.staffRanking()
    const names = res.map(r => r.staff_name).reverse()
    rankingChartInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['平均星级', '评价数', '完成工单'] },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: [
        { type: 'value', name: '星级', max: 5, position: 'top' },
        { type: 'value', name: '数量', position: 'bottom' }
      ],
      yAxis: { type: 'category', data: names },
      series: [
        {
          name: '平均星级', type: 'bar', xAxisIndex: 0,
          data: res.map(r => r.avg_rating).reverse(),
          itemStyle: {
            borderRadius: [0, 4, 4, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#ffd666' },
              { offset: 1, color: '#ff9900' }
            ])
          },
          label: { show: true, position: 'right', formatter: '{c}星' }
        },
        {
          name: '评价数', type: 'bar', xAxisIndex: 1,
          data: res.map(r => r.total_evaluations || r.total || 0).reverse(),
          itemStyle: { borderRadius: [0, 4, 4, 0], color: '#409EFF' },
          label: { show: true, position: 'right' }
        },
        {
          name: '完成工单', type: 'bar', xAxisIndex: 1,
          data: res.map(r => r.completed_orders || 0).reverse(),
          itemStyle: { borderRadius: [0, 4, 4, 0], color: '#67C23A' },
          label: { show: true, position: 'right' }
        }
      ]
    })
  } catch (error) {
    console.error(error)
  }
}

const updateTrendChart = async () => {
  try {
    const res = await evaluationApi.monthlyTrend()
    const data = res.reverse()
    trendChartInstance.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['评价数', '平均星级'] },
      xAxis: { type: 'category', data: data.map(d => d.month) },
      yAxis: [
        { type: 'value', name: '评价数' },
        { type: 'value', name: '星级', max: 5 }
      ],
      series: [
        { name: '评价数', type: 'bar', data: data.map(d => d.count) },
        { name: '平均星级', type: 'line', yAxisIndex: 1, data: data.map(d => d.avg_rating) }
      ]
    })
  } catch (error) {
    console.error(error)
  }
}

const updateDimensionCharts = async () => {
  try {
    const res = await evaluationApi.dimensionAnalysis()
    // 打印评价维度分析接口返回的原始数据，方便排查
    // console.log('dimension_analysis data:', res)
    if (!res) {
      setEmptyDimensionCharts()
      return
    }

    const createBarOption = (data, key, title) => {
      if (!data || !Array.isArray(data) || data.length === 0) return null
      const xData = data.map(d => `${d[key]}星`)
      const yData = data.map(d => d.count)
      return {
        title: { text: title + '评分分布', left: 'center', textStyle: { fontSize: 13, color: '#303133' } },
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { top: 50, bottom: 30, left: 45, right: 15, containLabel: false },
        xAxis: { type: 'category', data: xData, axisLabel: { color: '#606266' } },
        yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#606266' } },
        series: [{
          type: 'bar',
          barWidth: '50%',
          data: yData,
          itemStyle: {
            borderRadius: [4, 4, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#409EFF' },
              { offset: 1, color: '#79bbff' }
            ])
          },
          label: { show: true, position: 'top', color: '#303133', fontSize: 12 }
        }]
      }
    }

    const qualityOpt = createBarOption(res.quality_rating, 'quality_rating', '维修质量')
    const speedOpt = createBarOption(res.speed_rating, 'speed_rating', '响应速度')
    const attitudeOpt = createBarOption(res.attitude_rating, 'attitude_rating', '服务态度')

    if (qualityOpt && qualityChartInstance) {
      qualityChartInstance.setOption(qualityOpt, true)
    } else if (qualityChartInstance) {
      qualityChartInstance.setOption(getEmptyOption('暂无质量评分数据'), true)
    }

    if (speedOpt && speedChartInstance) {
      speedChartInstance.setOption(speedOpt, true)
    } else if (speedChartInstance) {
      speedChartInstance.setOption(getEmptyOption('暂无速度评分数据'), true)
    }

    if (attitudeOpt && attitudeChartInstance) {
      attitudeChartInstance.setOption(attitudeOpt, true)
    } else if (attitudeChartInstance) {
      attitudeChartInstance.setOption(getEmptyOption('暂无态度评分数据'), true)
    }
  } catch (e) {
    console.error('加载评分分布失败:', e)
    setEmptyDimensionCharts()
  }
}

const getEmptyOption = (text = '暂无数据') => ({
  title: { text, left: 'center', top: 'center', textStyle: { fontSize: 14, color: '#909399' } },
  xAxis: [],
  yAxis: [],
  series: []
})

const setEmptyDimensionCharts = () => {
  const emptyOpt = getEmptyOption()
  try { qualityChartInstance?.setOption(emptyOpt, true) } catch (_) {}
  try { speedChartInstance?.setOption(emptyOpt, true) } catch (_) {}
  try { attitudeChartInstance?.setOption(emptyOpt, true) } catch (_) {}
}

const viewDetail = (row) => {
  currentEvaluation.value = row
  detailVisible.value = true
}

const approveAppeal = (row) => {
  currentAppeal.value = row
  handleAppealType.value = 'approve'
  handleReply.value = ''
  handleAppealVisible.value = true
}

const rejectAppeal = (row) => {
  currentAppeal.value = row
  handleAppealType.value = 'reject'
  handleReply.value = ''
  handleAppealVisible.value = true
}

const submitHandleAppeal = async () => {
  handling.value = true
  try {
    if (handleAppealType.value === 'approve') {
      await appealApi.approve(currentAppeal.value.id, { reply: handleReply.value })
      ElMessage.success('申诉已通过，用户可重新评价')
    } else {
      await appealApi.reject(currentAppeal.value.id, { reply: handleReply.value })
      ElMessage.success('申诉已驳回')
    }
    handleAppealVisible.value = false
    loadAppeals()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    handling.value = false
  }
}

const getRatingType = (rating) => {
  if (rating >= 4) return 'success'
  if (rating >= 3) return 'warning'
  return 'danger'
}

const getAppealStatusType = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const getAppealStatusText = (status) => {
  const map = { pending: '待处理', approved: '已通过', rejected: '已驳回' }
  return map[status] || '未知状态'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped lang="scss">
.stat-card {
  text-align: center;
  padding: 20px;
  
  .stat-value {
    font-size: 32px;
    font-weight: bold;
    color: #303133;
    
    &.rating { color: #ff9900; }
    &.warning { color: #f56c6c; }
    &.appeal { color: #e6a23c; }
  }
  
  .stat-label {
    color: #909399;
    margin-top: 10px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 250px;
  min-height: 250px;
  position: relative;
}

.chart-container-lg {
  width: 100%;
  height: 300px;
  min-height: 300px;
  position: relative;
}
</style>
