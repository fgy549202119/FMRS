<!--
报修记录页面

该组件用于用户查看和管理自己的报修记录，包括：
- 报修记录列表展示
- 按状态筛选和关键词搜索
- 查看报修详情
- 取消待接单状态的报修
- 对已完成的工单进行评价

作者：范广宇
创建日期：2026年
-->
<template>
  <div class="page">
    <div class="page-header"><h2>报修记录</h2></div>

    <el-card>
      <div class="search-bar">
        <el-input v-model="searchKeyword" placeholder="搜索报修编号/设备名称" style="width: 200px; margin-right: 10px;" clearable />
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px; margin-right: 10px;">
          <el-option label="待接单" value="WAITING" />
          <el-option label="维修中" value="IN_PROGRESS" />
          <el-option label="待审核" value="PENDING_ADMIN_CLOSE" />
          <el-option label="已完成" value="CLOSED" />
          <el-option label="已驳回" value="REJECTED" />
        </el-select>
        <el-button type="primary" @click="loadData">搜索</el-button>
      </div>

      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column label="设备类型" width="120">
          <template #default="{ row }">{{ row.equipment_type_name || row.equipment_type || '-' }}</template>
        </el-table-column>
        <el-table-column label="设备位置" min-width="200">
          <template #default="{ row }">
            <div class="location-detail">
              <el-tag size="small" type="info" v-if="row.location">{{ row.location }}</el-tag>
              <el-tag size="small" type="info" v-if="row.building">{{ row.building }}</el-tag>
              <el-tag size="small" type="warning" v-if="row.floor">{{ row.floor }}层</el-tag>
              <el-tag size="small" type="success" v-if="row.room">{{ row.room }}</el-tag>
              <el-tag size="small" type="danger" v-if="row.equipment_sequence_number">序号{{ row.equipment_sequence_number }}</el-tag>
              <span v-if="!row.location && !row.building && !row.floor && !row.room">-</span>
            </div>
            <div v-if="row.location_detail" style="color: #909399; font-size: 12px; margin-top: 2px;">{{ row.location_detail }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }"><el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="staff_name" label="维修员" width="100"><template #default="{ row }">{{ row.staff_name || '未分配' }}</template></el-table-column>
        <el-table-column prop="created_at" label="报修时间" width="160"><template #default="{ row }">{{ formatDate(row.created_at) }}</template></el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="warning" link @click="handleCancel(row)" v-if="row.status === 'WAITING'">取消</el-button>
            <el-button type="success" link @click="handleEvaluate(row)" v-if="row.status === 'CLOSED' && !evaluatedOrderIds.has(row.id)">评价</el-button>
            <el-tag type="info" size="small" v-if="row.status === 'CLOSED' && evaluatedOrderIds.has(row.id)">已评价</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="currentPage" :page-size="pageSize" :total="total" layout="total, prev, pager, next" @current-change="loadData" />
    </el-card>

    <el-dialog v-model="viewVisible" title="报修详情" width="700px">
      <el-descriptions :column="2" border :label-width="100" v-if="currentItem">
        <el-descriptions-item label="报修编号">{{ currentItem.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="状态"><el-tag :type="getStatusType(currentItem.status)">{{ getStatusText(currentItem.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentItem.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentItem.equipment_type_name || currentItem.equipment_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="报修人">{{ currentItem.user_name }}</el-descriptions-item>
        <el-descriptions-item label="报修电话">{{ currentItem.user_phone || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ formatDate(currentItem.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="设备位置" :span="2">
          <template v-if="currentItem.location || currentItem.building || currentItem.floor || currentItem.room">
            <el-tag size="small" type="info" v-if="currentItem.location" style="margin-right:4px;">{{ currentItem.location }}</el-tag>
            <el-tag size="small" type="info" v-if="currentItem.building" style="margin-right:4px;">{{ currentItem.building }}</el-tag>
            <el-tag size="small" type="warning" v-if="currentItem.floor" style="margin-right:4px;">{{ currentItem.floor }}层</el-tag>
            <el-tag size="small" type="success" v-if="currentItem.room" style="margin-right:4px;">{{ currentItem.room }}</el-tag>
            <el-tag size="small" type="danger" v-if="currentItem.equipment_sequence_number" style="margin-right:4px;">序号{{ currentItem.equipment_sequence_number }}</el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="详细位置">{{ currentItem.location_detail || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="故障数量">{{ currentItem.fault_count || 1 }}</el-descriptions-item>
        <el-descriptions-item label="现场照片" :span="2">
          <div v-if="currentItem.scene_photos && currentItem.scene_photos.length > 0" class="scene-photos">
            <el-image v-for="(photo, idx) in currentItem.scene_photos" :key="idx" :src="photo" class="scene-photo-item" fit="cover" :preview-src-list="currentItem.scene_photos" :initial-index="idx" preview-teleported />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentItem.description || '无' }}</el-descriptions-item>
        <el-descriptions-item label="维修人" v-if="currentItem.status !== 'WAITING'">{{ currentItem.staff_name || '未分配' }}</el-descriptions-item>
        <el-descriptions-item label="维修电话" v-if="currentItem.status !== 'WAITING'">{{ currentItem.staff_phone || '未填写' }}</el-descriptions-item>
        <template v-if="currentItem.status !== 'WAITING'">
          <el-descriptions-item label="维修耗时">{{ currentItem.actual_duration ? formatDuration(currentItem.actual_duration) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="维修说明" :span="2">{{ currentItem.remark || '无' }}</el-descriptions-item>
          <el-descriptions-item label="维修照片" :span="2">
              <div v-if="currentItem.repair_photos && currentItem.repair_photos.length > 0" class="scene-photos">
                <el-image v-for="(photo, idx) in currentItem.repair_photos" :key="idx" :src="photo" class="scene-photo-item" fit="cover" :preview-src-list="currentItem.repair_photos" :initial-index="idx" preview-teleported />
              </div>
              <span v-else>无</span>
            </el-descriptions-item>
        </template>
      </el-descriptions>
      <template #footer><el-button @click="viewVisible = false">关闭</el-button><el-button type="danger" @click="handleCancelFromDetail" v-if="currentItem && currentItem.status === 'WAITING'">取消报修</el-button></template>
    </el-dialog>

    <el-dialog v-model="evaluateVisible" title="服务评价" width="500px">
      <div class="evaluation-form">
        <div class="order-info" v-if="currentOrder">
          <p><strong>报修编号：</strong>{{ currentOrder.repair_no }}</p>
          <p><strong>维修人员：</strong>{{ currentOrder.staff_name }}</p>
          <p><strong>设备名称：</strong>{{ currentOrder.equipment_name }}</p>
        </div>
        <el-divider />
        <div class="rating-section">
          <div class="rating-item"><span class="rating-label">维修质量</span><el-rate v-model="evaluateForm.quality_rating" show-text :texts="ratingTexts" /></div>
          <div class="rating-item"><span class="rating-label">响应速度</span><el-rate v-model="evaluateForm.speed_rating" show-text :texts="ratingTexts" /></div>
          <div class="rating-item"><span class="rating-label">服务态度</span><el-rate v-model="evaluateForm.attitude_rating" show-text :texts="ratingTexts" /></div>
        </div>
        <el-divider />
        <div class="overall-rating"><span class="rating-label">综合评分</span><el-rate v-model="overallRating" disabled show-score text-color="#ff9900" /></div>
        <el-input v-model="evaluateForm.content" type="textarea" :rows="4" placeholder="请输入评价内容（选填）" style="margin-top: 15px;" />
      </div>
      <template #footer><el-button @click="evaluateVisible = false">取消</el-button><el-button type="primary" @click="submitEvaluate" :loading="evaluating">提交评价</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { repairApi, evaluationApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const filterStatus = ref('')
const viewVisible = ref(false)
const currentItem = ref(null)
const evaluatedOrderIds = ref(new Set())

const evaluateVisible = ref(false)
const evaluating = ref(false)
const currentOrder = ref(null)
const ratingTexts = ['很差', '较差', '一般', '较好', '很好']

const evaluateForm = reactive({ quality_rating: 5, speed_rating: 5, attitude_rating: 5, content: '' })
const overallRating = computed(() => Math.round((evaluateForm.quality_rating + evaluateForm.speed_rating + evaluateForm.attitude_rating) / 3))

onMounted(async () => { await loadData() })

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await repairApi.orderList(params)
    tableData.value = res.results || []
    total.value = res.count || 0
    await loadEvaluatedStatus()
  } catch (error) { console.error(error) }
  finally { loading.value = false }
}

const loadEvaluatedStatus = async () => {
  const closedOrders = tableData.value.filter(r => r.status === 'CLOSED')
  if (closedOrders.length === 0) return
  try {
    const res = await evaluationApi.checkEvaluated(closedOrders.map(o => o.id).join(','))
    const ids = new Set(res.evaluated_order_ids || [])
    evaluatedOrderIds.value = ids
    tableData.value.forEach(order => { if (ids.has(order.id)) order.is_evaluated = true })
  } catch (e) { console.warn('加载评价状态失败', e) }
}

const handleView = async (row) => {
  // 列表接口现在是轻量返回，查看详情时再拉取单条详情，避免列表接口返回过大导致超时
  loading.value = true
  try {
    const detail = await repairApi.orderGet(row.id)
    currentItem.value = detail
    viewVisible.value = true
  } catch (e) {
    ElMessage.error(e?.response?.data?.message || e?.message || '加载详情失败')
  } finally {
    loading.value = false
  }
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm('确定取消该报修单？', '提示', { type: 'warning' })
  try { await repairApi.orderCancel(row.id); ElMessage.success('取消成功'); loadData() } catch (e) { ElMessage.error('取消失败') }
}
const handleCancelFromDetail = async () => {
  if (!currentItem.value) return
  await ElMessageBox.confirm('确定取消该报修单？', '提示', { type: 'warning' })
  try { await repairApi.orderCancel(currentItem.value.id); ElMessage.success('取消成功'); viewVisible.value = false; loadData() } catch (e) { ElMessage.error('取消失败') }
}

const handleEvaluate = (row) => {
  if (evaluatedOrderIds.value.has(row.id)) { ElMessage.warning('该工单已评价，不可重复评价'); return }
  currentOrder.value = row
  Object.assign(evaluateForm, { quality_rating: 5, speed_rating: 5, attitude_rating: 5, content: '' })
  evaluateVisible.value = true
}

const submitEvaluate = async () => {
  if (!currentOrder.value) return
  if (evaluatedOrderIds.value.has(currentOrder.value.id)) { ElMessage.warning('该工单已评价，不可重复评价'); return }
  evaluating.value = true
  try {
    await evaluationApi.create({
      repair_order: currentOrder.value.id,
      quality_rating: evaluateForm.quality_rating,
      speed_rating: evaluateForm.speed_rating,
      attitude_rating: evaluateForm.attitude_rating,
      content: evaluateForm.content
    })
    ElMessage.success('评价成功')
    evaluateVisible.value = false
    evaluatedOrderIds.value.add(currentOrder.value.id)
    loadData()
  } catch (e) { ElMessage.error(e.response?.data?.message || e.message || '评价失败') }
  finally { evaluating.value = false }
}

const parsePhotos = (photoStr) => {
  if (!photoStr) return []
  if (Array.isArray(photoStr)) return photoStr
  if (typeof photoStr === 'string' && photoStr.startsWith('[')) { try { return JSON.parse(photoStr) } catch (e) {} }
  if (typeof photoStr === 'string' && (photoStr.startsWith('data:') || photoStr.startsWith('http'))) return [photoStr]
  return [photoStr]
}

const getStatusType = (s) => ({ WAITING:'warning', IN_PROGRESS:'primary', PENDING_ADMIN_CLOSE:'info', CLOSED:'success', REJECTED:'danger' })[s] || 'info'
const getStatusText = (s) => ({ WAITING:'待接单', IN_PROGRESS:'处理中', PENDING_ADMIN_CLOSE:'待验收', CLOSED:'已完成', REJECTED:'已取消' })[s] || s
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : ''

const formatDuration = (minutes) => {
  if (!minutes) return '-'
  if (minutes < 60) return minutes + '分钟'
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  return m > 0 ? h + '小时' + m + '分' : h + '小时'
}
</script>

<style scoped lang="scss">
.search-bar { display: flex; align-items: center; margin-bottom: 20px; }
.location-detail { display: flex; gap: 4px; flex-wrap: wrap; align-items: center; }
.scene-photos { display: flex; gap: 8px; flex-wrap: wrap; }
.scene-photo-item { width: 150px; height: 110px; border-radius: 4px; overflow: hidden; flex-shrink: 0; }
.evaluation-form {
  .order-info p { margin: 8px 0; color: #666; }
  .rating-section .rating-item { display: flex; align-items: center; margin: 15px 0; .rating-label { width: 80px; font-weight: 500; } }
  .overall-rating { display: flex; align-items: center; .rating-label { width: 80px; font-weight: 500; } }
}
</style>
