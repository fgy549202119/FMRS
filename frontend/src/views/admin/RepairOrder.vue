<template>
  <div class="page">
    <div class="page-header"><h2>设备报修管理</h2></div>
    
    <el-card>
      <div class="search-bar">
        <el-select v-model="filterStatus" placeholder="状态筛选" clearable style="width: 120px; margin-right: 10px;">
          <el-option label="待接单" value="WAITING" />
          <el-option label="维修中" value="IN_PROGRESS" />
          <el-option label="待审核" value="PENDING_ADMIN_CLOSE" />
          <el-option label="已完成" value="CLOSED" />
          <el-option label="已驳回" value="REJECTED" />
        </el-select>
        <el-input v-model="searchKeyword" placeholder="搜索报修编号" style="width: 200px; margin-right: 10px;" clearable />
        <el-button type="primary" @click="loadData">搜索</el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="selectedRows.length === 0" style="margin-left: auto;">批量删除</el-button>
      </div>
      
      <el-table :data="tableData" stripe v-loading="loading" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="id" label="序号" width="60" />
        <el-table-column prop="repair_no" label="报修编号" width="150" />
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column label="设备类型" width="100">
          <template #default="{ row }">{{ row.equipment_type_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="设备位置" min-width="180">
          <template #default="{ row }">
            <span>{{ [row.location, row.building, row.floor, row.room].filter(Boolean).join(' ') || '-' }}</span>
            <el-tag size="small" type="danger" v-if="row.equipment_sequence_number" style="margin-left:4px;">序号{{ row.equipment_sequence_number }}</el-tag>
            <span v-if="row.location_detail" style="color:#909399;font-size:12px;">（{{ row.location_detail }}）</span>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="报修人" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="staff_name" label="维修员" width="100">
          <template #default="{ row }">
            {{ row.staff_name }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="报修时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="success" link @click="handleAssign(row)" v-if="row.status === 'WAITING'">分配</el-button>
            <el-button type="warning" link @click="handleReassign(row)" v-if="row.status === 'IN_PROGRESS'">转派</el-button>
            <el-button type="success" link @click="handleReview(row)" v-if="row.status === 'PENDING_ADMIN_CLOSE'">审核</el-button>
            <el-button type="danger" link @click="handleCancel(row)" v-if="row.status !== 'CLOSED'">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
      />
    </el-card>
    
    <el-dialog v-model="viewVisible" title="报修详情" width="700px">
      <el-descriptions :column="2" border v-if="currentItem" :label-width="100">
        <el-descriptions-item label="报修编号">{{ currentItem.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="工单状态"><el-tag :type="getStatusType(currentItem.status)">{{ getStatusText(currentItem.status) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="报修人">{{ currentItem.user_name }}</el-descriptions-item>
        <el-descriptions-item label="用户类型">{{ currentItem.user_type === 'teacher' ? '教师' : '学生' }}</el-descriptions-item>
        <el-descriptions-item label="报修电话">{{ currentItem.user_phone || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="报修时间">{{ formatDate(currentItem.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentItem.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ currentItem.equipment_type_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="设备位置" :span="2">
          <template v-if="currentItem.location || currentItem.building || currentItem.floor || currentItem.room">
            <el-tag size="small" type="info" v-if="currentItem.location" style="margin-right:4px;">{{ currentItem.location }}</el-tag>
            <el-tag size="small" type="info" v-if="currentItem.building" style="margin-right:4px;">{{ currentItem.building }}</el-tag>
            <el-tag size="small" type="warning" v-if="currentItem.floor" style="margin-right:4px;">{{ currentItem.floor }}层</el-tag>
            <el-tag size="small" type="success" v-if="currentItem.room">{{ currentItem.room }}</el-tag>
            <el-tag size="small" type="danger" v-if="currentItem.equipment_sequence_number" style="margin-left:4px;">序号{{ currentItem.equipment_sequence_number }}</el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="详细位置">{{ currentItem.location_detail || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="故障数量">{{ currentItem.fault_count || 1 }}</el-descriptions-item>
        <el-descriptions-item label="现场照片" :span="2">
          <div v-if="currentItem.scene_photos && currentItem.scene_photos.length > 0" style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-image v-for="(photo, idx) in currentItem.scene_photos" :key="idx" :src="photo" style="width:150px;height:110px;" fit="cover" :preview-src-list="currentItem.scene_photos" :initial-index="idx" preview-teleported />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="故障描述" :span="2">{{ currentItem.description || '无' }}</el-descriptions-item>
        <template v-if="currentItem.status !== 'WAITING'">
          <el-descriptions-item label="维修人员">{{ currentItem.staff_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="联系方式">{{ currentItem.staff_phone || '-' }}</el-descriptions-item>
        </template>
      </el-descriptions>
      <template #footer>
        <el-button @click="viewVisible = false">关闭</el-button>
        <el-button type="danger" @click="handleCancelFromDetail" v-if="currentItem && currentItem.status !== 'CLOSED'">取消工单</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="assignVisible" :title="assignMode === 'assign' ? '分配工单' : '转派工单（仅在线）'" width="400px">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="选择维修人员">
          <el-select v-model="assignForm.staff_id" placeholder="请选择维修员" style="width: 100%;">
            <el-option v-for="item in staffList" :key="item.id"
              :label="`${item.real_name} (${item.staff_no})`" :value="item.id"
              :disabled="assignMode === 'reassign' && !item.is_online" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAssign" :loading="assigning">确定</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="reviewVisible" title="维修审核" width="600px">
      <el-descriptions :column="2" border v-if="currentRecord" label-width="100px">
        <el-descriptions-item label="报修编号">{{ currentRecord.repair_no }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ currentRecord.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="维修人员">{{ currentRecord.staff_name }}</el-descriptions-item>
        <el-descriptions-item label="维修耗时">{{ currentRecord.actual_duration ? formatDuration(currentRecord.actual_duration) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="维修说明" :span="2">{{ currentRecord.remark || '无' }}</el-descriptions-item>
        <el-descriptions-item label="维修照片" :span="2">
          <div v-if="currentRecord.repair_photos && currentRecord.repair_photos.length > 0" style="display:flex;gap:8px;flex-wrap:wrap;">
            <el-image v-for="(photo, idx) in currentRecord.repair_photos" :key="idx" :src="photo" style="width:150px;height:110px;" fit="cover" :preview-src-list="currentRecord.repair_photos" />
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
        <el-descriptions-item label="使用备件" :span="2">
          <div v-if="currentRecord.spare_parts_info && currentRecord.spare_parts_info.length > 0">
            <el-table :data="currentRecord.spare_parts_info" size="small" style="width:100%;">
              <el-table-column prop="spare_part_name" label="备件名称" />
              <el-table-column prop="quantity" label="使用数量" />
            </el-table>
          </div>
          <span v-else>无</span>
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider />
      
      <el-form :model="reviewForm" label-width="80px">
        <el-form-item label="审核结果">
          <el-radio-group v-model="reviewForm.review_status">
            <el-radio label="approved">通过</el-radio>
            <el-radio label="rejected">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核回复">
          <el-input v-model="reviewForm.review_reply" type="textarea" :rows="3" placeholder="请输入审核回复（驳回时必填）" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="reviewing">提交审核</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { repairApi, staffApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { EventBus, Events } from '@/utils/eventBus'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const filterStatus = ref('')
const viewVisible = ref(false)
const currentItem = ref(null)
const selectedRows = ref([])

const assignVisible = ref(false)
const assignMode = ref('assign')
const assigning = ref(false)
const staffList = ref([])
const assignForm = reactive({
  staff_id: null,
  order_id: null
})

const reviewVisible = ref(false)
const reviewing = ref(false)
const currentRecord = ref(null)
const reviewForm = reactive({
  record_id: null,
  review_status: 'approved',
  review_reply: ''
})

onMounted(() => {
  loadData()
  loadStaffList()
  
  EventBus.on(Events.RECORD_DELETED, loadData)
  EventBus.on(Events.DATA_REFRESH, loadData)
})

onUnmounted(() => {
  EventBus.off(Events.RECORD_DELETED, loadData)
  EventBus.off(Events.DATA_REFRESH, loadData)
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, page_size: pageSize.value }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await repairApi.orderList(params)
    tableData.value = res.results || []
    total.value = res.count || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadStaffList = async (onlineOnly = false) => {
  try {
    if (onlineOnly) {
      const res = await repairApi.onlineStaffList()
      staffList.value = res.results || []
    } else {
      const res = await staffApi.list({ page_size: 100 })
      staffList.value = res.results || []
    }
  } catch (error) {
    console.error(error)
  }
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const handleView = async (row) => {
  try {
    const res = await repairApi.orderGet(row.id)
    currentItem.value = res
  } catch (e) {
    currentItem.value = row
  }
  viewVisible.value = true
}

const handleAssign = (row) => {
  assignMode.value = 'assign'
  assignForm.order_id = row.id
  assignForm.staff_id = null
  loadStaffList(true)
  assignVisible.value = true
}

const handleReassign = (row) => {
  assignMode.value = 'reassign'
  assignForm.order_id = row.id
  assignForm.staff_id = row.staff?.id || null
  loadStaffList(true)
  assignVisible.value = true
}

const submitAssign = async () => {
  if (!assignForm.staff_id) {
    ElMessage.warning('请选择维修员')
    return
  }
  assigning.value = true
  try {
    if (assignMode.value === 'assign') {
      await repairApi.orderTransfer(assignForm.order_id, { staff_id: assignForm.staff_id })
    } else {
      await repairApi.orderTransfer(assignForm.order_id, { staff_id: assignForm.staff_id })
    }
    ElMessage.success(assignMode.value === 'assign' ? '分配成功' : '转派成功')
    assignVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    assigning.value = false
  }
}

const handleCancel = async (row) => {
  await ElMessageBox.confirm('确定取消该报修单？', '提示', { type: 'warning' })
  try {
    await repairApi.orderCancel(row.id)
    ElMessage.success('取消成功')
    loadData()
  } catch (error) {
    ElMessage.error('取消失败')
  }
}

const handleCancelFromDetail = async () => {
  if (!currentItem.value) return
  await ElMessageBox.confirm('确定取消该报修单？', '提示', { type: 'warning' })
  try {
    await repairApi.orderCancel(currentItem.value.id)
    ElMessage.success('取消成功')
    viewVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('取消失败')
  }
}

const handleBatchDelete = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的报修单')
    return
  }
  await ElMessageBox.confirm(`确定删除选中的 ${selectedRows.value.length} 个报修单？此操作不可恢复！`, '警告', { type: 'warning' })
  try {
    for (const row of selectedRows.value) {
      await repairApi.orderDelete(row.id)
    }
    ElMessage.success('批量删除成功')
    loadData()
  } catch (error) {
    ElMessage.error('批量删除失败')
  }
}

const handleReview = async (row) => {
  try {
    const res = await repairApi.orderGet(row.id)
    currentRecord.value = res
  } catch (e) {
    currentRecord.value = { ...row }
  }
  reviewForm.record_id = row.id
  reviewForm.review_status = ''
  reviewForm.review_reply = ''
  reviewVisible.value = true
}

const submitReview = async () => {
  if (reviewForm.review_status === 'rejected' && !reviewForm.review_reply) {
    ElMessage.warning('驳回时请填写审核回复')
    return
  }
  
  reviewing.value = true
  try {
    await repairApi.orderReview(reviewForm.record_id, {
      review_status: reviewForm.review_status,
      review_reply: reviewForm.review_reply
    })
    ElMessage.success(reviewForm.review_status === 'approved' ? '审核通过' : '已驳回，维修员需重新维修')
    reviewVisible.value = false
    
    EventBus.emit(Events.DATA_REFRESH)
    if (reviewForm.review_status === 'approved') {
      EventBus.emit(Events.EQUIPMENT_CHANGED, { action: 'fault_count_updated' })
    }
    
    loadData()
  } catch (error) {
    ElMessage.error('审核失败')
  } finally {
    reviewing.value = false
  }
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

const formatDuration = (minutes) => {
  if (!minutes) return '-'
  if (minutes < 60) return minutes + '分钟'
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  return m > 0 ? h + '小时' + m + '分' : h + '小时'
}

const parsePhotos = (photoStr) => {
  if (!photoStr) return []
  if (Array.isArray(photoStr)) return photoStr
  if (typeof photoStr === 'string' && photoStr.startsWith('[')) { try { return JSON.parse(photoStr) } catch (e) {} }
  if (typeof photoStr === 'string' && (photoStr.startsWith('data:') || photoStr.startsWith('http'))) return [photoStr]
  return [photoStr]
}
</script>

<style scoped lang="scss">
.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
</style>
