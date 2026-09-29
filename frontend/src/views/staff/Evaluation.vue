<template>
  <div class="page">
    <div class="page-header"><h2>我的评价</h2></div>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value">{{ stats.total_count }}</div>
          <div class="stat-label">总评价数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value rating">{{ stats.avg_rating }}</div>
          <div class="stat-label">平均星级</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-value appeal">{{ stats.pending_appeal || 0 }}</div>
          <div class="stat-label">待处理申诉</div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>评价列表</span>
          <div class="filter-section">
            <el-date-picker
              v-model="selectedMonth"
              type="month"
              placeholder="选择月份"
              format="YYYY-MM"
              value-format="YYYY-MM"
              @change="loadEvaluations"
              clearable
            />
          </div>
        </div>
      </template>
      
      <el-table :data="evaluations" stripe v-loading="loading">
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column label="评分" width="280">
          <template #default="{ row }">
            <div class="rating-detail">
              <div class="rating-item">
                <span class="label">质量:</span>
                <el-rate v-model="row.quality_rating" disabled />
              </div>
              <div class="rating-item">
                <span class="label">速度:</span>
                <el-rate v-model="row.speed_rating" disabled />
              </div>
              <div class="rating-item">
                <span class="label">态度:</span>
                <el-rate v-model="row.attitude_rating" disabled />
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="综合" width="120">
          <template #default="{ row }">
            <el-tag :type="getRatingType(row.rating)" size="large">
              {{ row.rating }}星
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评价内容">
          <template #default="{ row }">
            {{ row.content || '无' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at_formatted" label="评价时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
            <el-tag v-if="getAppealTag(row)" :type="getAppealTag(row).type" size="small" effect="plain" style="margin-left:4px;">{{ getAppealTag(row).text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewOrder(row)">查看</el-button>
            <el-button type="warning" link size="small" @click="openAppeal(row)" v-if="canAppeal(row)">申诉</el-button>
            <el-button type="warning" link size="small" disabled v-else-if="row.appeal_status === 'approved'">申诉已通过</el-button>
            <el-button type="danger" link size="small" disabled v-else-if="row.appeal_status === 'rejected'">申诉已驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadEvaluations"
        style="margin-top: 20px; text-align: right;"
      />
    </el-card>
    
    <el-dialog v-model="orderDetailVisible" title="工单详情" width="600px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="报修编号">{{ currentOrder.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentOrder.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备位置" :span="2">
          <template v-if="currentOrder.location || currentOrder.building || currentOrder.floor || currentOrder.room">
            <el-tag size="small" type="info" v-if="currentOrder.location" style="margin-right:4px;">{{ currentOrder.location }}</el-tag>
            <el-tag size="small" type="info" v-if="currentOrder.building" style="margin-right:4px;">{{ currentOrder.building }}</el-tag>
            <el-tag size="small" type="warning" v-if="currentOrder.floor" style="margin-right:4px;">{{ currentOrder.floor }}层</el-tag>
            <el-tag size="small" type="success" v-if="currentOrder.room">{{ currentOrder.room }}</el-tag>
          </template>
          <span v-else>{{ currentOrder.location || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentOrder.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatDate(currentOrder.complete_time) }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    
    <el-dialog v-model="appealVisible" title="评价申诉" width="500px">
      <el-alert type="info" :closable="false" style="margin-bottom:16px;">
        <template #title>仅允许对评价时间在 3 天内的工单发起申诉</template>
      </el-alert>
      <el-form :model="appealForm" :rules="appealRules" ref="appealFormRef" label-width="80px">
        <el-form-item label="申诉理由" prop="reason">
          <el-input v-model="appealForm.reason" type="textarea" :rows="4" placeholder="请说明申诉理由" />
        </el-form-item>
        <el-form-item label="证据照片">
          <el-upload action="#" list-type="picture-card" :auto-upload="false" :limit="3" :on-change="handleAppealPhotoChange" :on-remove="handleAppealPhotoRemove" :file-list="appealPhotoList"><el-icon><Plus /></el-icon></el-upload>
          <div style="color:#999;font-size:12px;margin-top:4px;">最多上传3张证据照片</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="appealVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAppeal" :loading="appealing">提交申诉</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { evaluationApi, repairApi, appealApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const staffInfo = ref(JSON.parse(localStorage.getItem('staffInfo') || '{}'))
const loading = ref(false)
const evaluations = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const selectedMonth = ref('')
const stats = ref({
  total_count: 0,
  avg_rating: 0,
  avg_quality: 0,
  avg_speed: 0,
  avg_attitude: 0
})

const orderDetailVisible = ref(false)
const currentOrder = ref(null)

const appealVisible = ref(false)
const appealing = ref(false)
const appealFormRef = ref()
const appealPhotoList = ref([])
let appealPhotoBase64List = []
const appealForm = reactive({
  evaluation: null,
  reason: '',
  evidence: ''
})
const appealRules = {
  reason: [{ required: true, message: '请输入申诉理由', trigger: 'blur' }]
}

const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000

onMounted(() => {
  loadStats()
  loadEvaluations()
})

const canAppeal = (row) => {
  if (!row.created_at) return false
  if (row.is_hidden) return false
  if (row.appeal_status === 'approved') return false
  if (row.appeal_status === 'pending') return false
  if (row.appeal_status === 'rejected') return false
  try {
    const createdTime = new Date(row.created_at).getTime()
    return (Date.now() - createdTime) < THREE_DAYS_MS
  } catch {
    return false
  }
}

const getAppealTag = (row) => {
  if (row.is_hidden) return null
  if (row.appeal_status === 'approved') return { text: '已申诉', type: 'success' }
  if (row.appeal_status === 'pending') return { text: '申诉中', type: 'warning' }
  if (row.appeal_status === 'rejected') return { text: '已申诉', type: 'danger' }
  if (!row.created_at) return null
  try {
    const createdTime = new Date(row.created_at).getTime()
    if ((Date.now() - createdTime) < THREE_DAYS_MS) return { text: '可申诉', type: 'warning' }
    return { text: '已超时', type: 'info' }
  } catch {
    return null
  }
}

const loadStats = async () => {
  try {
    const res = await evaluationApi.statistics({})
    stats.value = res
  } catch (error) {
    console.error(error)
  }
}

const loadEvaluations = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (staffInfo.value.id) {
      params.staff = staffInfo.value.id
    }
    if (selectedMonth.value) {
      params.month = selectedMonth.value
    }
    const res = await evaluationApi.list(params)
    evaluations.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const viewOrder = async (row) => {
  try {
    if (!row.order_id) { ElMessage.error('关联工单信息缺失'); return }
    const res = await repairApi.orderGet(row.order_id)
    currentOrder.value = res
    orderDetailVisible.value = true
  } catch (error) {
    ElMessage.error('获取工单详情失败')
  }
}

const openAppeal = (evaluation) => {
  if (!canAppeal(evaluation)) {
    ElMessage.warning('该评价已超过3天，无法申诉')
    return
  }
  appealForm.evaluation = evaluation.id
  appealForm.reason = ''
  appealForm.evidence = ''
  appealPhotoList.value = []
  appealPhotoBase64List = []
  appealVisible.value = true
}

const handleAppealPhotoChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => { appealPhotoBase64List.push(e.target.result) }
  reader.readAsDataURL(file.raw)
}

const handleAppealPhotoRemove = () => {
  if (appealPhotoBase64List.length > 0) appealPhotoBase64List.pop()
}

const submitAppeal = async () => {
  await appealFormRef.value.validate()
  appealing.value = true
  try {
    const data = {
      evaluation: appealForm.evaluation,
      staff: staffInfo.value.id,
      reason: appealForm.reason
    }
    if (appealPhotoBase64List.length > 0) data.evidence = appealPhotoBase64List[0]
    await appealApi.create(data)
    ElMessage.success('申诉已提交，请等待管理员审核')
    appealVisible.value = false
    loadEvaluations()
  } catch (error) {
    const msg = error.response?.data?.message || error.response?.data?.detail || '提交失败'
    ElMessage.error(msg)
  } finally {
    appealing.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除该评价记录？', '提示', { type: 'warning' })
  try {
    await evaluationApi.delete(row.id)
    ElMessage.success('删除成功')
    loadEvaluations()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getRatingType = (rating) => {
  if (rating >= 4) return 'success'
  if (rating >= 3) return 'warning'
  return 'danger'
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
    &.quality { color: #67c23a; }
    &.speed { color: #409eff; }
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
  
  .filter-section {
    display: flex;
    gap: 10px;
  }
}

.rating-detail {
  .rating-item {
    display: flex;
    align-items: center;
    margin: 2px 0;
    
    .label {
      font-size: 12px;
      color: #666;
      width: 40px;
    }
  }
}
</style>
